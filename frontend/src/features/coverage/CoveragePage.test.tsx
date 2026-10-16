import { screen, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { meta } from "../../test/fixtures";
import { renderApp } from "../../test/render";
import { server } from "../../test/server";

test("the header says the page is not filtered, the six figures describe the database", async () => {
  renderApp("/coverage");
  expect(await screen.findByText("What is in the database. Not affected by the filters.")).toBeInTheDocument();
  const kpis = screen.getByLabelText("Key figures");
  for (const text of ["2", "556", "756", "967", "506", "0%", "above 10% a level filter would be needed"]) {
    expect(kpis).toHaveTextContent(text);
  }
});

test("competitions with dates, rank, level, ruleset, tagged scores and categories", async () => {
  renderApp("/coverage");
  const card = await screen.findByRole("region", { name: "Competitions loaded" });
  const row = within(card).getByRole("row", { name: /^Guadalajara Grand Prix 2025/ });
  for (const text of ["2025-10-17 → 2025-10-19", "Grand Prix", "Elite", "2025–", "98%", "28"]) {
    expect(row).toHaveTextContent(text);
  }
  expect(within(row).getByText("-66M")).toHaveAttribute("data-tip", "28 contests");
});

test("data quality issues with their contests, and an empty state without any", async () => {
  renderApp("/coverage");
  const card = await screen.findByRole("region", { name: "Data quality" });
  expect(within(card).getByRole("row", { name: /^IJF totals do not match the events/ })).toHaveTextContent("3");
});

test("no data quality issue: the card says so", async () => {
  server.use(http.get("/api/meta", () => HttpResponse.json({ ...meta, quality_issues: [] })));
  renderApp("/coverage");
  const card = await screen.findByRole("region", { name: "Data quality" });
  expect(card).toHaveTextContent("No known issue.");
});

test("excluded competitions start collapsed and give their reason", async () => {
  const { user } = renderApp("/coverage");
  const card = await screen.findByRole("region", { name: "Excluded competitions" });
  const summary = within(card).getByText("91 competitions excluded");
  expect(summary.closest("details")).not.toHaveAttribute("open");
  await user.click(summary);
  expect(summary.closest("details")).toHaveAttribute("open");
  const row = within(card).getByRole("row", { name: /Conegliano European Open 2025/ });
  expect(row).toHaveTextContent("Continental");
  expect(row).toHaveTextContent("technique tags on 0% of scores");
});

test("the glossary lists every term", async () => {
  renderApp("/coverage");
  const card = await screen.findByRole("region", { name: "Glossary" });
  expect(within(card).getAllByRole("row")).toHaveLength(meta.glossary.length);
});

test("the contests of each category are also in the page as text", async () => {
  renderApp("/coverage");
  const card = await screen.findByRole("region", { name: "Competitions loaded" });
  expect(within(card).getAllByText("28 contests")[0]).toHaveClass("sr");
});

test("no excluded competition: the card says so", async () => {
  server.use(http.get("/api/meta", () => HttpResponse.json({ ...meta, coverage: { ...meta.coverage, excluded: [] } })));
  renderApp("/coverage");
  expect(await screen.findByRole("region", { name: "Excluded competitions" })).toHaveTextContent(
    "No competition excluded.",
  );
});
