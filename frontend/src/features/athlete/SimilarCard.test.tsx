import { screen, waitFor, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { athlete, athleteAllWeights } from "../../test/fixtures";
import { currentParams, lastNavigation, renderApp } from "../../test/render";
import { server } from "../../test/server";

test("similar athletes of the same weight by default, as cards opening their page", async () => {
  renderApp("/athletes/900323?gender=m");
  const card = await screen.findByRole("region", { name: "Similar athletes" });
  expect(within(card).getByRole("button", { name: "Same weight (-66 M)" })).toHaveAttribute("aria-pressed", "true");
  const similar = within(card).getByRole("link", { name: /^Fomi DUGUMA/ });
  expect(similar).toHaveAttribute("href", "/athletes/900049?gender=m");
  for (const text of ["80%", "Kata-guruma 2 · Sasae-tsurikomi-ashi 2 · Hikikomi-gaeshi 1", "8 scores · small sample"]) {
    expect(similar).toHaveTextContent(text);
  }
});

test("All weights asks the API for every weight, replacing the history entry", async () => {
  const scopes: string[] = [];
  server.use(
    http.get("/api/athletes/:id", ({ request }) => {
      const scope = new URL(request.url).searchParams.get("similar_scope") ?? "";
      scopes.push(scope);
      return HttpResponse.json(scope === "all" ? athleteAllWeights : athlete);
    }),
  );
  const { user } = renderApp("/athletes/900323");
  const card = await screen.findByRole("region", { name: "Similar athletes" });
  await user.click(within(card).getByRole("button", { name: "All weights" }));
  expect(currentParams()).toEqual({ similar: "all" });
  expect(lastNavigation()).toBe("REPLACE");
  await waitFor(() => expect(scopes.at(-1)).toBe("all"));
});

test("no similar athlete in the weight: the empty state suggests All weights", async () => {
  const none = { ...athlete, data: { ...athlete.data, similar: { ...athlete.data.similar, rows: [] } } };
  server.use(http.get("/api/athletes/:id", () => HttpResponse.json(none)));
  renderApp("/athletes/900323");
  const card = await screen.findByRole("region", { name: "Similar athletes" });
  expect(card).toHaveTextContent("No similar athlete with at least 5 scores in this weight: try All weights.");
});
