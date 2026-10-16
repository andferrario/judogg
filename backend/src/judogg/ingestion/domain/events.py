from judogg.ingestion.domain.model import PenaltyKind, ScoreValue

SCORE_VALUES: dict[str, ScoreValue] = {"1": "ippon", "2": "waza_ari", "3": "waza_ari", "4": "yuko"}
# The contest summary counts awasete as a waza-ari.
SUMMARY_FIELDS: dict[str, str] = {"1": "ippon", "2": "waza", "3": "waza", "4": "yuko"}
PENALTY_KINDS: dict[str, PenaltyKind] = {"5": "shido", "7": "hansoku_shido"}
AWASETE = "2"
HANSOKU_SHIDO = "7"
NO_SCORE = "8"
# Type 6 (probably direct hansoku-make) was never observed: it stays unknown until verified.
KNOWN_EVENT_TYPES = frozenset({*SCORE_VALUES, *PENALTY_KINDS, NO_SCORE})
