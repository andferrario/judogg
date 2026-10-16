import { countChanged, FILTER_KEYS, toSearch, type FilterParams } from "./filters";

const STORAGE_KEY = "judogg-filters";

// Storage can be unavailable (private browsing, blocked site data): the URL alone then keeps the filters.
export function saveFilters(filters: FilterParams): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filters));
  } catch {
    return;
  }
}

export function savedFilters(): FilterParams {
  try {
    return pickFilters(JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "{}"));
  } catch {
    return {};
  }
}

function pickFilters(value: unknown): FilterParams {
  if (typeof value !== "object" || value === null) return {};
  const record = value as Record<string, unknown>;
  const filters: FilterParams = {};
  for (const key of FILTER_KEYS) {
    const item = record[key];
    if (typeof item === "string" && item) filters[key] = item;
  }
  return filters;
}

/** The search to open the app with: the saved filters when the URL has none, else `null`. */
export function searchWithSavedFilters(search: string): string | null {
  const params = new URLSearchParams(search);
  if (countChanged(params) > 0) return null;
  const saved = savedFilters();
  let restored = false;
  for (const key of FILTER_KEYS) {
    const value = saved[key];
    if (value) {
      params.set(key, value);
      restored = true;
    }
  }
  return restored ? toSearch(params) : null;
}
