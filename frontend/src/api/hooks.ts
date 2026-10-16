import { keepPreviousData, useQuery } from "@tanstack/react-query";
import type { FilterParams } from "../filters/filters";
import { api, unwrap } from "./client";

export function useMeta() {
  return useQuery({ queryKey: ["/api/meta"], queryFn: () => unwrap(api.GET("/api/meta")) });
}

// Query keys hold the params object as it is: TanStack Query hashes object keys in sorted order.
export function useOverview(filters: FilterParams) {
  return useQuery({
    queryKey: ["/api/overview", filters],
    queryFn: () => unwrap(api.GET("/api/overview", { params: { query: filters } })),
    placeholderData: keepPreviousData,
  });
}

export function useAthleteSearch(text: string) {
  const query = { q: text, limit: "8" };
  return useQuery({
    queryKey: ["/api/athletes", query],
    queryFn: () => unwrap(api.GET("/api/athletes", { params: { query } })),
    enabled: text.length >= 2,
    placeholderData: keepPreviousData,
  });
}

type TierQuery = { sort: string; order: string; limit: string };

export function useTechniques(filters: FilterParams, tier: TierQuery) {
  const query = { ...filters, ...tier };
  return useQuery({
    queryKey: ["/api/techniques", query],
    queryFn: () => unwrap(api.GET("/api/techniques", { params: { query } })),
    placeholderData: keepPreviousData,
  });
}

export function useWeightMatrix(filters: FilterParams) {
  return useQuery({
    queryKey: ["/api/techniques/by-weight", filters],
    queryFn: () => unwrap(api.GET("/api/techniques/by-weight", { params: { query: filters } })),
    placeholderData: keepPreviousData,
  });
}

export function useOutcomes(filters: FilterParams) {
  return useQuery({
    queryKey: ["/api/outcomes", filters],
    queryFn: () => unwrap(api.GET("/api/outcomes", { params: { query: filters } })),
    placeholderData: keepPreviousData,
  });
}

export function useTechnique(code: string | undefined, filters: FilterParams) {
  return useQuery({
    queryKey: ["/api/techniques/{code}", code, filters],
    queryFn: () => unwrap(api.GET("/api/techniques/{code}", { params: { path: { code: code ?? "" }, query: filters } })),
    enabled: code !== undefined,
    placeholderData: keepPreviousData,
  });
}

type ScoreListQuery = { score_value?: string; page: string; page_size: string };

export function useTechniqueScores(code: string, filters: FilterParams, list: ScoreListQuery) {
  const query = { ...filters, ...list };
  return useQuery({
    queryKey: ["/api/techniques/{code}/scores", code, query],
    queryFn: () => unwrap(api.GET("/api/techniques/{code}/scores", { params: { path: { code }, query } })),
    placeholderData: keepPreviousData,
  });
}

export function useRepertoire(code: string | undefined, filters: FilterParams, withCode?: string) {
  const query = { ...filters, technique: code ?? "", with: withCode };
  return useQuery({
    queryKey: ["/api/repertoire", query],
    queryFn: () => unwrap(api.GET("/api/repertoire", { params: { query } })),
    enabled: code !== undefined,
    placeholderData: keepPreviousData,
  });
}

export function useCounters(code: string, filters: FilterParams) {
  const query = { ...filters, technique: code };
  return useQuery({
    queryKey: ["/api/counters", query],
    queryFn: () => unwrap(api.GET("/api/counters", { params: { query } })),
    placeholderData: keepPreviousData,
  });
}

export function useRepertoirePairs(filters: FilterParams) {
  return useQuery({
    queryKey: ["/api/repertoire/pairs", filters],
    queryFn: () => unwrap(api.GET("/api/repertoire/pairs", { params: { query: filters } })),
    placeholderData: keepPreviousData,
  });
}

export function usePenalties(filters: FilterParams) {
  return useQuery({
    queryKey: ["/api/penalties", filters],
    queryFn: () => unwrap(api.GET("/api/penalties", { params: { query: filters } })),
    placeholderData: keepPreviousData,
  });
}

type AthleteQuery = { similar_scope: string; min_scores_athlete?: string };

export function useAthlete(id: string, query: AthleteQuery) {
  return useQuery({
    queryKey: ["/api/athletes/{athlete_id}", id, query],
    queryFn: () => unwrap(api.GET("/api/athletes/{athlete_id}", { params: { path: { athlete_id: id }, query } })),
    placeholderData: keepPreviousData,
  });
}
