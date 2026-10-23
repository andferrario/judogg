import { screen, waitFor, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { overview } from "../test/fixtures";
import { currentParams, lastNavigation, renderApp } from "../test/render";
import { server } from "../test/server";

const group = (name: string | RegExp) => screen.findByRole("group", { name });

test("the data strip shows the totals of the current filters", async () => {
  renderApp("/techniques");
  const strip = await screen.findByRole("status", { name: "In this filter" });
  await waitFor(() => expect(strip).toHaveTextContent("2 competitions"));
  for (const text of ["556 contests", "506 judoka", "756 scores", "967 penalties"]) {
    expect(strip).toHaveTextContent(text);
  }
});

test("a total of one is singular", async () => {
  const totals = { competitions: 1, contests: 1, athletes: 1, scores: 1, penalties: 1 };
  server.use(http.get("/api/overview", () => HttpResponse.json({ ...overview, totals })));
  renderApp("/techniques");
  const strip = await screen.findByRole("status", { name: "In this filter" });
  await waitFor(() => expect(strip).toHaveTextContent("1 competition1 contest1 judoka1 score1 penalty"));
});

test.each([
  ["/coverage", "Coverage is not filtered."],
  ["/athletes/900323", "The judoka page is not filtered: it shows the athlete's whole career."],
])("%s has no data strip and no filter controls", async (url, note) => {
  renderApp(url);
  expect(await screen.findByText(note, { exact: false })).toBeInTheDocument();
  expect(screen.queryByRole("status", { name: "In this filter" })).not.toBeInTheDocument();
  expect(screen.queryByRole("group", { name: "Gender" })).not.toBeInTheDocument();
});

test("a gender click replaces the history entry; All is the default and is not written", async () => {
  const { user } = renderApp("/techniques");
  const gender = await group("Gender");
  await user.click(within(gender).getByRole("button", { name: "Men" }));
  expect(currentParams()).toEqual({ gender: "m" });
  expect(lastNavigation()).toBe("REPLACE");
  await user.click(within(gender).getByRole("button", { name: "All" }));
  expect(currentParams()).toEqual({});
});

test("a gender change drops the weights of the other gender", async () => {
  const { user } = renderApp("/techniques?weight=m-73,f-57");
  await user.click(within(await group("Gender")).getByRole("button", { name: "Women" }));
  expect(currentParams()).toEqual({ gender: "f", weight: "f-57" });
});

test("weight chips toggle categories and All clears them", async () => {
  const { user } = renderApp("/techniques");
  const weight = await group("Weight");
  await user.click(within(weight).getByRole("button", { name: "-73M" }));
  await user.click(within(weight).getByRole("button", { name: "-81M" }));
  expect(currentParams()).toEqual({ weight: "m-73,m-81" });
  expect(within(weight).getByRole("button", { name: "-73M" })).toHaveAttribute("aria-pressed", "true");
  await user.click(within(weight).getByRole("button", { name: "All" }));
  expect(currentParams()).toEqual({});
});

test("with one gender the chips show only its categories, without the initial", async () => {
  renderApp("/techniques?gender=f");
  const weight = await group("Weight");
  expect(within(weight).getAllByRole("button").map((chip) => chip.textContent)).toEqual([
    "All",
    "-48",
    "-52",
    "-57",
    "-63",
    "-70",
    "-78",
    "+78",
  ]);
});

test("a ruleset change clears the years", async () => {
  const { user } = renderApp("/techniques?year_from=2026");
  await user.click(within(await group(/^Ruleset/)).getByRole("button", { name: "2018–2024" }));
  expect(currentParams()).toEqual({ ruleset: "2017,2025" });
});

test("the years offer only years with contests, From never after To", async () => {
  const { user } = renderApp("/techniques");
  const from = await screen.findByLabelText("From");
  expect(within(from).getAllByRole("option").map((option) => option.textContent)).toEqual(["2025", "2026"]);
  await user.selectOptions(from, "2026");
  expect(currentParams()).toEqual({ year_from: "2026" });
  const to = screen.getByLabelText("To");
  expect(within(to).getAllByRole("option").map((option) => option.textContent)).toEqual(["2026"]);
});

test("choosing the first or last year offered removes the bound: it is the default", async () => {
  const { user } = renderApp("/techniques");
  await user.selectOptions(await screen.findByLabelText("From"), "2026");
  await user.selectOptions(screen.getByLabelText("From"), "2025");
  expect(currentParams()).toEqual({});
  await user.selectOptions(screen.getByLabelText("To"), "2025");
  expect(currentParams()).toEqual({ year_to: "2025" });
  await user.selectOptions(screen.getByLabelText("To"), "2026");
  expect(currentParams()).toEqual({});
});

test("any filter change restarts the scores list and keeps the other page parameters", async () => {
  const { user } = renderApp("/techniques?trend=uchi_mata&v_page=3");
  await user.selectOptions(await screen.findByLabelText("Athlete country"), "JPN");
  expect(currentParams()).toEqual({ trend: "uchi_mata", country: "JPN" });
});

test("unchecking a side lists the others; checking it back removes the filter", async () => {
  const { user } = renderApp("/techniques");
  await user.click(await screen.findByRole("checkbox", { name: "Unknown" }));
  expect(currentParams()).toEqual({ side: "left,right" });
  await user.click(screen.getByRole("checkbox", { name: "Unknown" }));
  expect(currentParams()).toEqual({});
});

test("technique type and count by", async () => {
  const { user } = renderApp("/techniques");
  await user.click(within(await group(/^Technique type/)).getByRole("button", { name: "Ground" }));
  await user.click(within(await group("Count by")).getByRole("button", { name: "Athlete" }));
  expect(currentParams()).toEqual({ domain: "ground", count_by: "athlete" });
});

test("a minimum is written on Enter; an out-of-range value is refused", async () => {
  const { user } = renderApp("/techniques");
  const input = await screen.findByLabelText("Min. scores per athlete");
  await user.clear(input);
  await user.type(input, "8{Enter}");
  expect(currentParams()).toEqual({ min_scores_athlete: "8" });
  await user.clear(input);
  await user.type(input, "99{Enter}");
  expect(input).toHaveValue(8);
  expect(currentParams()).toEqual({ min_scores_athlete: "8" });
});

test("the summary counts the filters in the URL; Reset removes them and keeps the page parameters", async () => {
  const { user } = renderApp("/techniques?gender=m&weight=m-73&trend=uchi_mata&v_page=2");
  expect(await screen.findByText("2 changed")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Reset filters" }));
  expect(currentParams()).toEqual({ trend: "uchi_mata" });
  expect(screen.queryByText(/changed$/)).not.toBeInTheDocument();
});

test("a hand-edited URL with unknown values does not break the rail", async () => {
  renderApp("/techniques?ruleset=9999&year_from=abc&gender=x");
  expect(await screen.findByLabelText("From")).toBeDisabled();
  expect(within(await group("Weight")).getAllByRole("button").map((chip) => chip.textContent)).toEqual(["All"]);
});
