import math
from collections import Counter
from collections.abc import Sequence
from typing import cast

from judogg.ingestion.domain.constants import WEIGHT_CATEGORY_IDS
from judogg.ingestion.domain.events import (
    AWASETE,
    HANSOKU_SHIDO,
    KNOWN_EVENT_TYPES,
    NO_SCORE,
    PENALTY_KINDS,
    SCORE_VALUES,
    SUMMARY_FIELDS,
)
from judogg.ingestion.domain.model import (
    Athlete,
    Competition,
    Contest,
    ContestDims,
    EndType,
    Gender,
    ParsedContest,
    Penalty,
    QualityIssue,
    RawJson,
    Score,
    SkippedContest,
    Tag,
)
from judogg.ingestion.domain.tags import WIN_TYPE_GROUP, WIN_TYPES, direction, tag_kind, technique_domain, to_tag

# Issues that make the contest's numbers doubtful.
QUALITY_CODES = frozenset({"summary_mismatch", "unknown_event_type", "unknown_actor"})

# Contest summary fields, recomputed from the events to detect IJF data errors.
SUMMARY_KEYS = ("ippon_w", "waza_w", "yuko_w", "penalty_w", "ippon_b", "waza_b", "yuko_b", "penalty_b")


def parse_contest(raw: RawJson, competition: Competition) -> ParsedContest | SkippedContest:
    if raw["age"] != "Seniors":
        return SkippedContest(f"age {raw['age']}")
    if raw.get("id_fight_team") is not None:
        return SkippedContest("team contest")
    if raw["is_finished"] != "1":
        return SkippedContest("not finished")
    contest_id = int(raw["id_fight"])
    gender = str(raw["contest_code_long"]).split("_")[-3]  # the contest has no gender field
    weight = str(raw["weight"]).strip()
    if weight.lower() == "open":
        return SkippedContest("open weight")  # expected: no quality issue
    category_id = WEIGHT_CATEGORY_IDS.get(f"{gender}{weight}")
    if category_id is None:
        issue = QualityIssue("unknown_weight", contest_id, None, {"gender": gender, "weight": weight})
        return SkippedContest("unknown weight", issue)
    dims = ContestDims(competition.id, competition.year, competition.ruleset_id, cast(Gender, gender), category_id)
    durations = _durations(raw)
    if durations is None:
        return SkippedContest("unreadable duration")
    if raw.get("country_short_white") is None or raw.get("country_short_blue") is None:
        return SkippedContest("missing country")
    return _ContestParser(raw, contest_id, dims, *durations).parse()


def sorted_events(events: Sequence[RawJson]) -> list[RawJson]:
    """IJF event ids are not chronological: they only break ties."""
    return sorted(events, key=lambda e: (_number(e.get("time_sc")), _number(e.get("time_real")), int(e["id_event"])))


def _number(value: object) -> float:
    return float(str(value)) if value is not None else 0.0


def _durations(raw: RawJson) -> tuple[int, int] | None:
    """Contest duration and regular duration in seconds, or None when either is unreadable."""
    try:
        return _seconds(raw["duration"]), int(raw["fight_duration"])
    except TypeError, ValueError:
        return None


def _name(value: object) -> str:
    return str(value) if value is not None else ""


def _seconds(hms: object) -> int:
    hours, minutes, seconds = (int(part) for part in str(hms).split(":"))
    return hours * 3600 + minutes * 60 + seconds


def _competitor_count(event: RawJson) -> int:
    return len({actor["id_person"] for actor in event.get("actors") or [] if actor["actor_type"] == "competitor"})


class _ContestParser:
    def __init__(self, raw: RawJson, contest_id: int, dims: ContestDims, duration_s: int, regular_s: int) -> None:
        self.duration_s = duration_s
        self.regular_s = regular_s
        self.raw = raw
        self.contest_id = contest_id
        self.dims = dims
        self.white = int(raw["id_person_white"])
        self.blue = int(raw["id_person_blue"])
        self.side = {self.white: "w", self.blue: "b"}
        self.country = {self.white: str(raw["country_short_white"]), self.blue: str(raw["country_short_blue"])}
        self.scores: list[Score] = []
        self.penalties: list[Penalty] = []
        self.tags: dict[int, Tag] = {}
        self.issues: list[QualityIssue] = []
        self.recomputed: Counter[str] = Counter()
        self.shidos: Counter[int] = Counter()
        self.win_types: set[str] = set()

    def parse(self) -> ParsedContest:
        events = sorted_events(self.raw.get("events") or [])
        for event in events:
            self._event(event)
        self._check_summary()
        went_gs = (
            self.raw["gs"] == "1"
            or any(event.get("is_gs") == "1" for event in events)
            or self.duration_s > self.regular_s
        )
        processed = [event for event in events if event["id_contest_event_type"] != NO_SCORE]
        contest = Contest(
            id=self.contest_id,
            code=str(self.raw["contest_code_long"]),
            dims=self.dims,
            white_athlete_id=self.white,
            blue_athlete_id=self.blue,
            white_country_code=self.country[self.white],
            blue_country_code=self.country[self.blue],
            end_type=self._end_type(processed, went_gs),
            went_gs=went_gs,
            duration_s=self.duration_s,
            has_quality_issue=any(issue.code in QUALITY_CODES for issue in self.issues),
        )
        athletes = (
            Athlete(
                self.white,
                _name(self.raw["family_name_white"]),
                _name(self.raw["given_name_white"]),
                self.country[self.white],
            ),
            Athlete(
                self.blue,
                _name(self.raw["family_name_blue"]),
                _name(self.raw["given_name_blue"]),
                self.country[self.blue],
            ),
        )
        return ParsedContest(
            contest=contest,
            athletes=athletes,
            scores=tuple(self.scores),
            penalties=tuple(self.penalties),
            tags=tuple(self.tags.values()),
            issues=tuple(self.issues),
            n_events=len(events),
        )

    def _event(self, event: RawJson) -> None:
        event_id = int(event["id_event"])
        event_type = str(event["id_contest_event_type"])
        if event_type not in KNOWN_EVENT_TYPES:
            self.issues.append(QualityIssue("unknown_event_type", self.contest_id, event_id, {"type": event_type}))
            return
        if event_type == NO_SCORE:
            return  # the cancelled score is already gone from the events: nothing to subtract
        raw_tags: Sequence[RawJson] = event.get("tags") or []
        self._collect_tags(event_id, raw_tags)
        win_type = next((str(t["code_short"]) for t in raw_tags if str(t["id_group"]) == WIN_TYPE_GROUP), None)
        if win_type is not None and win_type not in WIN_TYPES:
            self.issues.append(
                QualityIssue(
                    "new_tag_group", self.contest_id, event_id, {"id_group": WIN_TYPE_GROUP, "code_short": win_type}
                )
            )
        athletes = self._competitors(event_id, event)
        if event_type in SCORE_VALUES:
            self._score(event, event_id, event_type, raw_tags, athletes, win_type)
        else:
            self._penalty(event, event_id, event_type, raw_tags, athletes)

    def _score(
        self,
        event: RawJson,
        event_id: int,
        event_type: str,
        raw_tags: Sequence[RawJson],
        athletes: list[int],
        win_type: str | None,
    ) -> None:
        for athlete in athletes:
            self.recomputed[f"{SUMMARY_FIELDS[event_type]}_{self.side[athlete]}"] += 1
        if win_type is not None:
            self.win_types.add(win_type)
            return  # walkovers and withdrawals are not scores
        # one row per distinct technique: a tag repeated in one event is still one technique
        distinct = {int(t["id_tag"]): t for t in raw_tags if tag_kind(t) == "technique"}
        techniques: list[RawJson | None] = list(distinct.values()) or [None]
        side = direction(raw_tags)
        is_gs, time_bin = self._timing(event)
        for athlete in athletes:
            opponent = self.blue if athlete == self.white else self.white
            for technique in techniques:  # one row per technique of a combination
                self.scores.append(
                    Score(
                        event_id=event_id,
                        contest_id=self.contest_id,
                        dims=self.dims,
                        athlete_id=athlete,
                        athlete_country=self.country[athlete],
                        opponent_id=opponent,
                        score_value=SCORE_VALUES[event_type],
                        is_awasete=event_type == AWASETE,
                        technique_tag_id=int(technique["id_tag"]) if technique else None,
                        technique_domain=technique_domain(technique) if technique else "unknown",
                        direction=side,
                        is_gs=is_gs,
                        time_bin=time_bin,
                    )
                )

    def _penalty(
        self, event: RawJson, event_id: int, event_type: str, raw_tags: Sequence[RawJson], athletes: list[int]
    ) -> None:
        reason = next((int(t["id_tag"]) for t in raw_tags if tag_kind(t) == "shido_reason"), None)
        is_gs, time_bin = self._timing(event)
        for athlete in athletes:
            side = self.side[athlete]
            self.recomputed[f"penalty_{side}"] += 1
            if event_type == HANSOKU_SHIDO and len(athletes) == 1:
                # the opponent's ippon exists only in the summary: there is no ippon event
                self.recomputed[f"ippon_{'b' if side == 'w' else 'w'}"] += 1
            self.shidos[athlete] += 1
            self.penalties.append(
                Penalty(
                    event_id=event_id,
                    contest_id=self.contest_id,
                    dims=self.dims,
                    athlete_id=athlete,
                    athlete_country=self.country[athlete],
                    penalty_kind=PENALTY_KINDS[event_type],
                    shido_number=self.shidos[athlete],
                    reason_tag_id=reason,
                    is_gs=is_gs,
                    time_bin=time_bin,
                )
            )

    def _check_summary(self) -> None:
        for key in SUMMARY_KEYS:
            summary = int(self.raw.get(key) or 0)
            if summary != self.recomputed[key]:
                self.issues.append(
                    QualityIssue(
                        "summary_mismatch",
                        self.contest_id,
                        None,
                        {"field": key, "summary": summary, "events": self.recomputed[key]},
                    )
                )

    def _competitors(self, event_id: int, event: RawJson) -> list[int]:
        athletes = []
        for actor in event.get("actors") or []:
            if actor["actor_type"] != "competitor":
                continue
            person = int(actor["id_person"])
            if person not in self.side:
                self.issues.append(QualityIssue("unknown_actor", self.contest_id, event_id, {"id_person": person}))
                continue
            if person in athletes:
                continue  # a competitor listed twice is still one athlete scoring or penalised
            athletes.append(person)
        return athletes

    def _collect_tags(self, event_id: int, raw_tags: Sequence[RawJson]) -> None:
        for raw_tag in raw_tags:
            if tag_kind(raw_tag) is None:
                continue
            tag = to_tag(raw_tag)
            if tag.group_label is None:
                self.issues.append(
                    QualityIssue("new_tag_group", self.contest_id, event_id, {"id_group": str(raw_tag["id_group"])})
                )
            self.tags[tag.id] = tag

    @staticmethod
    def _timing(event: RawJson) -> tuple[bool, int]:
        """`time_real_gs` is unreliable: golden score comes from `is_gs` only."""
        is_gs = event.get("is_gs") == "1"
        return is_gs, 8 if is_gs else min(7, max(0, math.floor(_number(event.get("time_sc")) / 30)))

    def _end_type(self, events: Sequence[RawJson], went_gs: bool) -> EndType:
        types = {str(event["id_contest_event_type"]) for event in events}
        if "fusen_gachi" in self.win_types:
            return "fusen_gachi"
        if "kiken_gachi" in self.win_types:
            return "kiken_gachi"
        if any(
            str(event["id_contest_event_type"]) == HANSOKU_SHIDO and _competitor_count(event) == 2 for event in events
        ):
            return "double_hansoku"
        if "1" in types:
            return "ippon"
        if "2" in types:
            return "waza_ari_awasete"
        if HANSOKU_SHIDO in types:
            return "hansoku_shido"
        return "score_gs" if went_gs else "score_regulation"
