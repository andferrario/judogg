import { screen, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { uchiMataDetail } from "../../test/fixtures";
import { renderApp } from "../../test/render";
import { server } from "../../test/server";

test("by weight: the technique's share of each weight with its side, small weights greyed", async () => {
  renderApp("/techniques/uchi_mata");
  const card = await screen.findByRole("region", { name: "By weight" });
  const [first, second] = within(card).getAllByRole("listitem");
  expect(first).toHaveTextContent("-60 M");
  expect(first).toHaveAttribute("data-sample", "insufficient");
  expect(second).toHaveTextContent("4.0%");
  expect(within(second).getByRole("img", { name: "Left 2 · Right 3 · Unknown 0" })).toBeInTheDocument();
});

test("when it scores: the blocks of this technique", async () => {
  renderApp("/techniques/uchi_mata");
  const card = await screen.findByRole("region", { name: "When it scores" });
  expect(within(card).getByRole("img", { name: "Scores with Uchi-mata per 30-second block" })).toBeInTheDocument();
});

test("trend: two years are an insufficient sample, shown greyed", async () => {
  renderApp("/techniques/uchi_mata");
  const card = await screen.findByRole("region", { name: "Trend" });
  expect(card).toHaveAttribute("data-sample", "insufficient");
  expect(card).toHaveTextContent("2025: 4.8% (2 of 42)");
});

test("countries: the lift of each country, the threshold in the description", async () => {
  renderApp("/techniques/uchi_mata");
  const card = await screen.findByRole("region", { name: "Countries" });
  const [japan] = within(card).getAllByRole("listitem");
  expect(japan).toHaveTextContent("JPN");
  expect(japan).toHaveTextContent("1.3");
  expect(card).toHaveTextContent("at least 30 scores");
  expect(within(card).getByRole("button", { name: "About Lift" })).toBeInTheDocument();
});

test("countries: an empty state when no country reaches the threshold", async () => {
  const detail = { ...uchiMataDetail, data: { ...uchiMataDetail.data, countries: { rows: [], min_scores_country: 30 } } };
  server.use(http.get("/api/techniques/:code", () => HttpResponse.json(detail)));
  renderApp("/techniques/uchi_mata");
  const card = await screen.findByRole("region", { name: "Countries" });
  expect(card).toHaveTextContent("No country with at least 30 scores in the filter.");
});
