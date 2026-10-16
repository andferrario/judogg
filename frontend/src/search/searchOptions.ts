import type { Meta, SearchRow } from "../api/types";
import { athleteName, weightLabel } from "../format/format";

export type SearchOption = {
  id: string;
  label: string;
  detail: string;
  pathname: string;
  extra?: Record<string, string>;
};

// "uchi mata", "Uchi-Mata" and "uchi-matá" all find Uchi-mata.
export function normalise(text: string): string {
  return text.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase().replaceAll("-", " ").trim();
}

export function athleteOptions(rows: readonly SearchRow[]): SearchOption[] {
  return rows.map(({ athlete, weights }) => ({
    id: `athlete-${athlete.id}`,
    label: athleteName(athlete),
    detail: [athlete.country_code, weights.map(weightLabel).join(", ")].join(" · "),
    pathname: `/athletes/${athlete.id}`,
  }));
}

export function catalogueOptions(meta: Meta, text: string): SearchOption[] {
  const query = normalise(text);
  if (!query) return [];
  const matches = (name: string) => normalise(name).includes(query);
  const techniques = meta.techniques
    .filter((technique) => matches(technique.name))
    .map((technique) => ({
      id: `technique-${technique.code}`,
      label: technique.name,
      detail: detail("Technique", technique.group_label),
      pathname: `/techniques/${technique.code}`,
    }));
  const reasons = meta.shido_reasons
    .filter((reason) => matches(reason.name))
    .map((reason) => ({
      id: `reason-${reason.code}`,
      label: reason.name,
      detail: detail("Shido reason", reason.group_label),
      pathname: "/penalties",
      extra: { reason: reason.code },
    }));
  return [...techniques, ...reasons];
}

function detail(kind: string, group: string | null): string {
  return group ? `${kind} · ${group}` : kind;
}
