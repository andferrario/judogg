import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import type { ReactNode } from "react";
import { athlete } from "../test/fixtures";
import { server } from "../test/server";
import { useAthlete, usePenalties, useRepertoire, useRepertoirePairs } from "./hooks";
import { createQueryClient } from "./queryClient";

function wrapper({ children }: { children: ReactNode }) {
  return <QueryClientProvider client={createQueryClient()}>{children}</QueryClientProvider>;
}

test("the repertoire waits until a technique is known", () => {
  const { result } = renderHook(() => useRepertoire(undefined, {}), { wrapper });
  expect(result.current.fetchStatus).toBe("idle");
});

test("the repertoire sends the companion when there is one", async () => {
  const { result } = renderHook(() => useRepertoire("seoi_nage", {}, "o_uchi_gari"), { wrapper });
  await waitFor(() => expect(result.current.data?.data.pair_athletes?.technique.code).toBe("o_uchi_gari"));
});

test("pairs and penalties come from their endpoints", async () => {
  const pairs = renderHook(() => useRepertoirePairs({}), { wrapper });
  const penalties = renderHook(() => usePenalties({}), { wrapper });
  await waitFor(() => expect(pairs.result.current.data?.data.eligible).toBe(111));
  await waitFor(() => expect(penalties.result.current.data?.data.kpis.n_shido).toBe(910));
});

test("the judoka hook sends only its own parameters", async () => {
  const queries: Record<string, string>[] = [];
  server.use(
    http.get("/api/athletes/:id", ({ request }) => {
      queries.push(Object.fromEntries(new URL(request.url).searchParams));
      return HttpResponse.json(athlete);
    }),
  );
  renderHook(() => useAthlete("900323", { similar_scope: "all", min_scores_athlete: "3" }), { wrapper });
  await waitFor(() => expect(queries).toEqual([{ similar_scope: "all", min_scores_athlete: "3" }]));
});
