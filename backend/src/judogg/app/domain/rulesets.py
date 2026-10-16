from collections.abc import Iterable

from judogg.app.domain.model import Ruleset


def default_ruleset(rulesets: Iterable[Ruleset]) -> Ruleset | None:
    """The most recent ruleset with contests; without contests, the most recent one."""
    ordered = sorted(rulesets, key=lambda r: r.year_from, reverse=True)
    return next((r for r in ordered if r.contests), next(iter(ordered), None))
