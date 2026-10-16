import type { ApiFilters, Defaults, Meta, WeightOption } from "../api/types";
import { DOMAIN_LABEL } from "../format/format";

export const FILTER_KEYS = [
  "gender",
  "weight",
  "ruleset",
  "year_from",
  "year_to",
  "country",
  "side",
  "domain",
  "count_by",
  "min_scores_athlete",
  "min_scores_technique",
] as const;

export type FilterKey = (typeof FILTER_KEYS)[number];
export type FilterParams = Partial<Record<FilterKey, string>>;
/** `null` or `""` removes the parameter. */
export type FilterChange = Partial<Record<FilterKey, string | null>>;
export type YearRange = { years: number[]; from: number | undefined; to: number | undefined };

const SIDES = ["left", "right", "unknown"];
const GENDER_LABEL: Record<ApiFilters["gender"], string> = { all: "Men and women", m: "Men", f: "Women" };

export function isFilterKey(key: string): key is FilterKey {
  return (FILTER_KEYS as readonly string[]).includes(key);
}

export function readFilters(params: URLSearchParams): FilterParams {
  const filters: FilterParams = {};
  for (const key of FILTER_KEYS) {
    const value = params.get(key);
    if (value) filters[key] = value;
  }
  return filters;
}

// Commas are legal in a query string: unescaped, the lists stay readable in the address bar.
export function toSearch(params: URLSearchParams): string {
  const text = params.toString().replaceAll("%2C", ",");
  return text ? `?${text}` : "";
}

export function filterSearch(params: URLSearchParams, extra: Record<string, string> = {}): string {
  const next = new URLSearchParams();
  for (const [key, value] of params) if (isFilterKey(key)) next.set(key, value);
  for (const [key, value] of Object.entries(extra)) next.set(key, value);
  return toSearch(next);
}

export function listParam(params: URLSearchParams, key: string): string[] {
  return (params.get(key) ?? "").split(",").filter(Boolean);
}

export function toggleValue(list: readonly string[], value: string): string[] {
  return list.includes(value) ? list.filter((item) => item !== value) : [...list, value];
}

export function changeFilters(params: URLSearchParams, change: FilterChange, defaults: Defaults): URLSearchParams {
  const next = new URLSearchParams(params);
  for (const key of FILTER_KEYS) {
    if (!(key in change)) continue;
    const value = change[key];
    if (!value || isDefault(key, value, defaults)) next.delete(key);
    else next.set(key, value);
  }
  // Page N of the scores list under the old filters means nothing under the new ones.
  next.delete("v_page");
  return next;
}

function isDefault(key: FilterKey, value: string, defaults: Defaults): boolean {
  switch (key) {
    case "gender":
      return value === defaults.gender;
    case "count_by":
      return value === defaults.count_by;
    case "min_scores_athlete":
      return value === String(defaults.min_scores_athlete);
    case "min_scores_technique":
      return value === String(defaults.min_scores_technique);
    case "ruleset":
      return sameMembers(value.split(","), defaults.ruleset.map(String));
    default:
      return false;
  }
}

function sameMembers(first: readonly string[], second: readonly string[]): boolean {
  return first.length === second.length && first.every((item) => second.includes(item));
}

export function resetFilters(params: URLSearchParams): URLSearchParams {
  const next = new URLSearchParams(params);
  for (const key of FILTER_KEYS) next.delete(key);
  next.delete("v_page");
  return next;
}

export function countChanged(params: URLSearchParams): number {
  return FILTER_KEYS.filter((key) => params.get(key)).length;
}

// The API rejects a weight category of the other gender.
export function genderChange(params: URLSearchParams, gender: string, weights: readonly WeightOption[]): FilterChange {
  const genderOf = new Map(weights.map((weight) => [weight.code, weight.gender]));
  const kept = listParam(params, "weight").filter((code) => gender === "all" || genderOf.get(code) === gender);
  return { gender, weight: kept.join(",") };
}

export function selectedRulesets(params: URLSearchParams, defaults: Defaults): string[] {
  const selected = listParam(params, "ruleset");
  return selected.length ? selected : defaults.ruleset.map(String);
}

// The years of the old rulesets may not exist in the new ones.
export function rulesetToggle(params: URLSearchParams, id: string, defaults: Defaults): FilterChange {
  const ruleset = toggleValue(selectedRulesets(params, defaults), id).join(",");
  return { ruleset, year_from: null, year_to: null };
}

export function sideChange(params: URLSearchParams, side: string, checked: boolean): string | null {
  const current = listParam(params, "side");
  const selected = current.length ? current : SIDES;
  const next = SIDES.filter((item) => (item === side ? checked : selected.includes(item)));
  return next.length === SIDES.length || next.length === 0 ? null : next.join(",");
}

export function yearRange(params: URLSearchParams, meta: Meta): YearRange {
  const ids = selectedRulesets(params, meta.defaults).map(Number);
  const rulesets = meta.rulesets.filter((ruleset) => ids.includes(ruleset.id));
  const first = Math.min(...rulesets.map((ruleset) => ruleset.year_from));
  const last = Math.max(...rulesets.map((ruleset) => ruleset.year_to));
  const years = meta.years.filter((year) => year >= first && year <= last);
  return {
    years,
    from: yearParam(params, "year_from") ?? years.at(0),
    to: yearParam(params, "year_to") ?? years.at(-1),
  };
}

// The first and last years offered are the API's own bounds: choosing one removes the parameter.
export function yearChange(range: YearRange, key: "year_from" | "year_to", value: string): FilterChange {
  const bound = key === "year_from" ? range.years.at(0) : range.years.at(-1);
  return { [key]: value === String(bound) ? null : value };
}

function yearParam(params: URLSearchParams, key: string): number | undefined {
  const text = params.get(key);
  if (!text) return undefined;
  const year = Number(text);
  return Number.isInteger(year) ? year : undefined;
}

export function filterSummary(filters: ApiFilters, meta: Meta): string {
  const rulesetLabel = (id: number) => meta.rulesets.find((ruleset) => ruleset.id === id)?.label ?? String(id);
  const weightLabel = (code: string) => meta.weights.find((weight) => weight.code === code)?.label ?? code;
  const parts = [
    GENDER_LABEL[filters.gender],
    filters.weight.length ? `${filters.weight.map(weightLabel).join(", ")} kg` : "all weights",
    `rules ${filters.ruleset.map(rulesetLabel).join(", ")}`,
  ];
  if (filters.year_from !== null && filters.year_to !== null) {
    parts.push(
      filters.year_from === filters.year_to ? String(filters.year_from) : `${filters.year_from}–${filters.year_to}`,
    );
  }
  if (filters.country.length) parts.push(filters.country.join(", "));
  if (filters.domain.length < 3) parts.push(filters.domain.map((domain) => DOMAIN_LABEL[domain]).join("/"));
  if (filters.side.length < 3) parts.push(`side ${filters.side.join("/")}`);
  return parts.join(" · ");
}

export type ParamChange = Record<string, string | null>;

export function changeParams(params: URLSearchParams, change: ParamChange): URLSearchParams {
  const next = new URLSearchParams(params);
  for (const [key, value] of Object.entries(change)) {
    if (value) next.set(key, value);
    else next.delete(key);
  }
  return next;
}
