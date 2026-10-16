import { screen, waitFor, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { athlete } from "../../test/fixtures";
import { renderApp } from "../../test/render";
import { server } from "../../test/server";

test("the header names the athlete, their country, categories, years and JudoBase profile", async () => {
  renderApp("/athletes/900323?gender=m");
  expect(await screen.findByRole("heading", { level: 1, name: "Tagi SADIDI" })).toHaveAttribute("data-big");
  const profile = screen.getByRole("link", { name: "JudoBase profile ↗" });
  expect(profile).toHaveAttribute("href", "https://judobase.ijf.org/#/competitor/profile/900323");
  expect(profile.closest("p")).toHaveTextContent("AZE · -66 M 9 contests · 2025–2026 · JudoBase profile ↗");
  expect(screen.getByText("Whole career in the database, not filtered. Results and contest list: JudoBase.")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "← Techniques" })).toHaveAttribute("href", "/techniques?gender=m");
});

test("the KPIs", async () => {
  renderApp("/athletes/900323");
  const kpis = await screen.findByLabelText("Key figures");
  for (const text of ["10", "in 9 contests · 2 competitions", "7", "50%", "most scores"]) {
    expect(kpis).toHaveTextContent(text);
  }
  expect(within(kpis).getByRole("link", { name: "Sasae-tsurikomi-ashi" })).toHaveAttribute(
    "href",
    "/techniques/sasae_tsurikomi_ashi",
  );
});

test("an unknown athlete: Not found, the header still readable", async () => {
  renderApp("/athletes/1");
  expect(await screen.findByRole("alert")).toHaveTextContent("Not found. unknown athlete 1");
  expect(screen.getByRole("heading", { level: 1, name: "Judoka" })).toBeInTheDocument();
});

test("the page is not filtered: only its own parameters reach the API", async () => {
  const queries: Record<string, string>[] = [];
  server.use(
    http.get("/api/athletes/:id", ({ request }) => {
      queries.push(Object.fromEntries(new URL(request.url).searchParams));
      return HttpResponse.json(athlete);
    }),
  );
  renderApp("/athletes/900323?gender=f&weight=f-57&min_scores_athlete=3&similar=all");
  await waitFor(() => expect(queries).toEqual([{ similar_scope: "all", min_scores_athlete: "3" }]));
});

test("a malformed athlete id: Not found", async () => {
  server.use(
    http.get("/api/athletes/:id", () =>
      HttpResponse.json({ error: { code: "not_found", message: "unknown athlete abc", field: "athlete" } }, { status: 404 }),
    ),
  );
  renderApp("/athletes/abc");
  expect(await screen.findByRole("alert")).toHaveTextContent("Not found. unknown athlete abc");
  expect(screen.getByRole("heading", { level: 1, name: "Judoka" })).toBeInTheDocument();
});
