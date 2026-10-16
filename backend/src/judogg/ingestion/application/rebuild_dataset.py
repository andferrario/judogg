from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from judogg.ingestion.application.errors import LoadError
from judogg.ingestion.application.ports import DatasetRepository, RawResponseRepository
from judogg.ingestion.application.raw_responses import COMPETITION_LIST
from judogg.ingestion.domain.competitions import (
    ExclusionRules,
    InvalidCompetitionEntry,
    RulesetConflict,
    build_competitions,
    is_competition_list,
    read_entry,
)
from judogg.ingestion.domain.inclusion import decide_inclusion, reason_kind
from judogg.ingestion.domain.model import Competition, ParsedContest, QualityIssue, RawJson, SkippedContest
from judogg.ingestion.domain.parser import parse_contest


@dataclass(frozen=True)
class LoadSummary:
    table_counts: Mapping[str, int]
    included: int
    excluded: tuple[tuple[str, str], ...]  # (competition name, reason)
    issues: Mapping[str, int]
    skipped: Mapping[str, int]  # per reason
    without_contests: tuple[str, ...]  # contest data, but every contest skipped
    excluded_per_reason: Mapping[str, int]
    new_tag_groups: tuple[str, ...]  # "32", or "121 (hantei)" for an unknown win type


class RebuildDataset:
    def __init__(self, raw: RawResponseRepository, dataset: DatasetRepository, rules: ExclusionRules) -> None:
        self._raw = raw
        self._dataset = dataset
        self._rules = rules

    def execute(self) -> LoadSummary:
        listing = self._raw.get(COMPETITION_LIST, {})
        if listing is None:
            raise LoadError("the competitions list is not stored: run fetch, or load --files, first")
        if not is_competition_list(listing):
            raise LoadError("the stored competitions list is not a list of competitions: run fetch again")
        try:
            listed = {read_entry(raw, lambda r: int(r["id_competition"])) for raw in listing}
            competitions, rulesets = build_competitions(listing, self._rules)
        except (InvalidCompetitionEntry, RulesetConflict) as error:
            raise LoadError(f"competitions list: {error}") from error
        by_id = {c.id: c for c in competitions}
        with_data = self._raw.contest_competition_ids()
        unlisted = sorted(set(with_data) - listed)
        if unlisted:
            raise LoadError(f"contest data of competitions not in the competitions list: {unlisted}")
        to_parse = sorted(
            (by_id[i] for i in with_data if i in by_id and by_id[i].exclusion_reason is None),
            key=lambda c: (c.date_from, c.id),
        )  # competitions before the history start are not in by_id
        by_rule = sorted(
            (by_id[i] for i in with_data if i in by_id and by_id[i].exclusion_reason is not None),
            key=lambda c: (c.date_from, c.id),
        )
        excluded = [(c.name, c.exclusion_reason or "") for c in by_rule]
        per_reason: Counter[str] = Counter(reason for _, reason in excluded)
        new_groups: set[str] = set()
        issues: Counter[str] = Counter()
        skipped: Counter[str] = Counter()
        without_contests: list[str] = []
        seen: set[int] = set()
        with self._dataset.rebuild() as writer:
            writer.add_rulesets(rulesets)
            writer.add_competitions(competitions)
            for competition in to_parse:
                parsed, skips = self._parse(competition, seen)
                skipped.update(skip.reason for skip in skips)
                inclusion = decide_inclusion(parsed)
                writer.set_inclusion(competition.id, inclusion)
                kind = reason_kind(inclusion)
                if kind is not None:
                    excluded.append((competition.name, inclusion.exclusion_reason or kind))
                    per_reason[kind] += 1
                    continue
                if not inclusion.contests:
                    without_contests.append(competition.name)
                skip_issues = [skip.issue for skip in skips if skip.issue is not None]
                writer.add_contests(inclusion.contests)
                writer.add_issues([*skip_issues, *inclusion.issues])
                written = [*(i for c in inclusion.contests for i in c.issues), *skip_issues, *inclusion.issues]
                issues.update(i.code for i in written)
                new_groups.update(_tag_group(i) for i in written if i.code == "new_tag_group")
        included = len(to_parse) - (len(excluded) - len(by_rule)) - len(without_contests)
        return LoadSummary(
            self._dataset.table_counts(),
            included,
            tuple(excluded),
            dict(issues),
            dict(skipped),
            tuple(without_contests),
            dict(per_reason),
            tuple(sorted(new_groups)),
        )

    def _parse(self, competition: Competition, seen: set[int]) -> tuple[list[ParsedContest], list[SkippedContest]]:
        parsed: list[ParsedContest] = []
        skipped: list[SkippedContest] = []
        for payload in self._raw.contest_payloads(competition.id):
            for raw in _contests_of(payload):
                fight = int(raw["id_fight"])
                if fight in seen:
                    raise LoadError(f"contest {fight} appears twice in the raw responses")
                seen.add(fight)
                try:
                    result = parse_contest(raw, competition)
                except Exception as error:
                    raise LoadError(
                        f"competition {competition.id} ({competition.name}), "
                        f"contest {raw.get('contest_code_long')}: {error!r}"
                    ) from error
                if isinstance(result, ParsedContest):
                    parsed.append(result)
                else:
                    skipped.append(result)
        return sorted(parsed, key=lambda p: p.contest.id), skipped


def _tag_group(issue: QualityIssue) -> str:
    code = issue.detail.get("code_short")
    return f"{issue.detail['id_group']} ({code})" if code else str(issue.detail["id_group"])


def _contests_of(payload: Any) -> Iterable[RawJson]:
    """`contest.find` returns `{"contests": [...]}`, or `[]` when a category has no contest."""
    if isinstance(payload, dict):
        contests: list[RawJson] = payload.get("contests") or []
        return contests
    return []
