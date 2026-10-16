import type { Athlete, WeightRef } from "../api/types";

const MISSING = "–";

export function formatCount(value: number | null): string {
  return value === null ? MISSING : value.toLocaleString("en-US");
}

export function formatPercent(share: number | null, decimals = 0): string {
  return share === null ? MISSING : `${(share * 100).toFixed(decimals)}%`;
}

export function formatDecimal(value: number | null, decimals = 2): string {
  return value === null ? MISSING : value.toFixed(decimals);
}

export function formatDuration(seconds: number | null): string {
  if (seconds === null) return MISSING;
  const whole = Math.round(seconds);
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, "0")}`;
}

export function weightLabel(weight: WeightRef): string {
  return `${weight.label} ${weight.gender === "m" ? "M" : "W"}`;
}

export function athleteName(athlete: Athlete): string {
  return `${athlete.given_name} ${athlete.family_name}`;
}

export const VALUE_LABEL = { ippon: "Ippon", waza_ari: "Waza-ari", yuko: "Yuko" } as const;

export const END_LABEL = {
  ippon: "Ippon",
  waza_ari_awasete: "Waza-ari awasete ippon",
  hansoku_shido: "Hansoku-make (3rd shido)",
  double_hansoku: "Double hansoku-make",
  score_gs: "Score in golden score",
  score_regulation: "Score in regulation time",
} as const;

export const DOMAIN_LABEL = { standing: "Standing", ground: "Ground", unknown: "Unknown" } as const;

const BLOCK_STARTS = ["0:00", "0:30", "1:00", "1:30", "2:00", "2:30", "3:00", "3:30"];

export function formatTimeBin(timeBin: number, isGs: boolean): string {
  return isGs ? "GS" : `${BLOCK_STARTS[timeBin] ?? "?"}+`;
}

export const SIDE_LABEL = { left: "Left", right: "Right", unknown: "Unknown" } as const;
