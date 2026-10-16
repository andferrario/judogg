from collections.abc import Sequence

from judogg.ingestion.domain.model import Direction, Domain, RawJson, Tag, TagKind, TechniqueDomain
from judogg.ingestion.domain.names import normalise_name

# id_group -> (label, domain). The IJF API only gives numeric ids: the labels are ours.
GROUP_LABELS: dict[str, tuple[str, Domain | None]] = {
    "29": ("Ashi-waza", "standing"),
    "30": ("Koshi-waza", "standing"),
    "31": ("Ma-sutemi-waza", "standing"),
    "33": ("Te-waza", "standing"),
    "35": ("Yoko-sutemi-waza", "standing"),
    "24": ("Kansetsu-waza", "ground"),
    "25": ("Osaekomi-waza", "ground"),
    "27": ("Shime-waza", "ground"),
    "111": ("Grip", None),
    "112": ("Passivity", None),
    "113": ("Infractions", None),
    "114": ("Other", None),
}
STANDING_GROUP = "28"
GROUND_GROUP = "23"
SHIDO_REASON_GROUP = "110"
WIN_TYPE_GROUP = "121"
SIDE_GROUP = "126"
WIN_TYPES = frozenset({"fusen_gachi", "kiken_gachi"})


def tag_kind(raw_tag: RawJson) -> TagKind | None:
    groups = str(raw_tag["id_groups"]).split(",")
    if STANDING_GROUP in groups or GROUND_GROUP in groups:
        return "technique"
    if SHIDO_REASON_GROUP in groups:
        return "shido_reason"
    return None


def to_tag(raw_tag: RawJson) -> Tag:
    for field in ("code_short", "name"):
        if raw_tag.get(field) is None:
            raise ValueError(f"tag {raw_tag['id_tag']} has no {field}")
    kind = tag_kind(raw_tag)
    if kind is None:
        raise ValueError(f"tag {raw_tag['code_short']} is neither a technique nor a shido reason")
    label = GROUP_LABELS.get(str(raw_tag["id_group"]))
    return Tag(
        id=int(raw_tag["id_tag"]),
        code=str(raw_tag["code_short"]),
        name=normalise_name(str(raw_tag["name"])),
        kind=kind,
        group_label=label[0] if label else None,
        domain=label[1] if label and kind == "technique" else None,
    )


def technique_domain(raw_tag: RawJson) -> TechniqueDomain:
    label = GROUP_LABELS.get(str(raw_tag["id_group"]))
    return label[1] if label and label[1] else "unknown"


def direction(raw_tags: Sequence[RawJson]) -> Direction:
    side = next((str(t["code_short"]) for t in raw_tags if str(t["id_group"]) == SIDE_GROUP), None)
    if side == "left":
        return "left"
    if side == "right":
        return "right"
    return "unknown"
