import { screen, waitFor, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { pairs, pairsNone, repertoireSeoiNage } from "../../test/fixtures";
import { currentParams, lastNavigation, renderApp } from "../../test/render";
import { server } from "../../test/server";

function recordRepertoireQueries() {
  const queries: Record<string, string>[] = [];
  server.use(
    http.get("/api/repertoire", ({ request }) => {
      queries.push(Object.fromEntries(new URL(request.url).searchParams));
      return HttpResponse.json(repertoireSeoiNage);
    }),
  );
  return queries;
}

test("without a technique in the URL the page waits for the lift matrix and opens its first technique", async () => {
  const queries = recordRepertoireQueries();
  renderApp("/repertoire");
  await waitFor(() => expect(screen.getByLabelText("Technique")).toHaveValue("seoi_nage"));
  await waitFor(() => expect(queries).toHaveLength(1));
  expect(queries[0]).toMatchObject({ technique: "seoi_nage" });
});

test("when the lift matrix fails, the first technique of the metadata is used", async () => {
  server.use(http.get("/api/repertoire/pairs", () => new HttpResponse(null, { status: 500 })));
  const queries = recordRepertoireQueries();
  renderApp("/repertoire");
  await waitFor(() => expect(queries[0]).toMatchObject({ technique: "ashi_guruma" }));
});

test("the header explains the cohort and the thresholds", async () => {
  renderApp("/repertoire?technique=seoi_nage");
  expect(
    await screen.findByText(
      "23 athletes with at least 2 scores · a technique is in an athlete's repertoire with at least 1 score. Scores, not attempts: this is “also score with”, not combinations within one action.",
    ),
  ).toBeInTheDocument();
});

test("the three figures", async () => {
  renderApp("/repertoire?technique=seoi_nage");
  const kpis = await screen.findByLabelText("Key figures");
  expect(within(kpis).getByText("Eligible athletes").closest("div")).toHaveTextContent("23");
  expect(within(kpis).getByText("With Seoi-nage").closest("div")).toHaveTextContent("10");
  expect(within(kpis).getByText("Companions").closest("div")).toHaveTextContent("20");
});

test("companions: share of the cohort, usual share, lift; a row opens its athletes", async () => {
  const { user } = renderApp("/repertoire?technique=seoi_nage&gender=m");
  const card = await screen.findByRole("region", { name: "Seoi-nage → also score with" });
  const row = within(card).getByRole("row", { name: /^Yoko-shiho-gatame/ });
  for (const text of ["40%", "26%", "1.53"]) expect(row).toHaveTextContent(text);
  expect(row).toHaveAttribute("data-sample", "insufficient");
  await user.click(within(row).getByRole("link", { name: "Yoko-shiho-gatame" }));
  expect(currentParams()).toEqual({ gender: "m", technique: "seoi_nage", with: "yoko_shiho_gatame" });
  expect(lastNavigation()).toBe("REPLACE");
});

test("the chosen companion is highlighted and its athletes are listed", async () => {
  renderApp("/repertoire?technique=seoi_nage&with=o_uchi_gari");
  const companions = await screen.findByRole("region", { name: "Seoi-nage → also score with" });
  expect(within(companions).getByRole("row", { name: /^O-uchi-gari/ })).toHaveAttribute("data-selected");
  const pair = screen.getByRole("region", { name: "Seoi-nage + O-uchi-gari" });
  const row = within(pair).getByRole("row", { name: /^Vezo VAVOKU/ });
  for (const text of ["-66 M", "2", "3", "11"]) expect(row).toHaveTextContent(text);
  expect(within(row).getByRole("link", { name: "Vezo VAVOKU" })).toHaveAttribute("href", "/athletes/900413");
});

test("before a companion is chosen, the athletes card says what to do", async () => {
  renderApp("/repertoire?technique=seoi_nage");
  const card = await screen.findByRole("region", { name: "Athletes" });
  expect(card).toHaveTextContent("Pick a companion technique to see the athletes behind it.");
});

test("another technique drops the companion of the old one", async () => {
  const { user } = renderApp("/repertoire?technique=seoi_nage&with=o_uchi_gari");
  await user.selectOptions(await screen.findByLabelText("Technique"), "uchi_mata");
  expect(currentParams()).toEqual({ technique: "uchi_mata" });
  expect(lastNavigation()).toBe("REPLACE");
});

test("a filter change without a technique waits for the new lift matrix instead of asking for the old technique", async () => {
  const queries: Record<string, string>[] = [];
  server.use(
    http.get("/api/repertoire/pairs", ({ request }) =>
      HttpResponse.json(new URL(request.url).searchParams.get("gender") === "f" ? pairsNone : pairs),
    ),
    http.get("/api/repertoire", ({ request }) => {
      queries.push(Object.fromEntries(new URL(request.url).searchParams));
      return HttpResponse.json(repertoireSeoiNage);
    }),
  );
  const { user } = renderApp("/repertoire");
  await waitFor(() => expect(queries).toHaveLength(1));
  await user.click(within(screen.getByRole("group", { name: "Gender" })).getByRole("button", { name: "Women" }));
  await waitFor(() => expect(queries).toHaveLength(2));
  expect(queries[1]).toMatchObject({ gender: "f", technique: "o_uchi_gari" });
  await new Promise((resolve) => setTimeout(resolve, 200));
  expect(queries).toHaveLength(2);
});
