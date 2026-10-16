const ALL = ["ippon", "waza_ari", "yuko"];

/** The new selection (`[]` = all values), or `null` when the click would leave none. */
export function toggleScoreValue(selected: readonly string[], value: string): string[] | null {
  const current = selected.length ? selected : ALL;
  if (current.includes(value)) {
    if (current.length === 1) return null;
    return current.filter((item) => item !== value);
  }
  const next = ALL.filter((item) => item === value || current.includes(item));
  return next.length === ALL.length ? [] : next;
}
