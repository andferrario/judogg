import { screen, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { tierList } from "../../test/fixtures";
import { server } from "../../test/server";
import { currentParams, lastNavigation, renderApp } from "../../test/render";

test("when scores happen: nine blocks, golden score apart, values readable", async () => {
  renderApp("/techniques");
  const card = await screen.findByRole("region", { name: "When scores happen" });
  expect(within(card).getByRole("img", { name: "Scores per 30-second block" })).toBeInTheDocument();
  expect(card).toHaveTextContent("Golden score: 102 scores (Ippon 24, Waza-ari 29, Yuko 49)");
  expect(card).toHaveTextContent("Counts, not rates");
});

test("the trend follows the first technique of the tier list", async () => {
  renderApp("/techniques");
  const card = await screen.findByRole("region", { name: "Trend" });
  expect(within(card).getByLabelText("Technique of the trend")).toHaveValue("seoi_nage");
  expect(await within(card).findByText("2025: 11.9% (5 of 42)")).toBeInTheDocument();
  expect(within(card).getByText("insufficient · n=2")).toBeInTheDocument();
});

test("choosing another technique writes it in the URL, replacing the entry", async () => {
  const { user } = renderApp("/techniques");
  const card = await screen.findByRole("region", { name: "Trend" });
  await user.selectOptions(within(card).getByLabelText("Technique of the trend"), "uchi_mata");
  expect(currentParams()).toEqual({ trend: "uchi_mata" });
  expect(lastNavigation()).toBe("REPLACE");
  expect(await within(card).findByText("2026: 7.0% (50 of 714)")).toBeInTheDocument();
});

test("a trend technique not in the tier list falls back to the first row", async () => {
  renderApp("/techniques?trend=nope");
  const card = await screen.findByRole("region", { name: "Trend" });
  expect(within(card).getByLabelText("Technique of the trend")).toHaveValue("seoi_nage");
});

test("without any technique in the tier list the trend card says so", async () => {
  const onlyUnknown = { ...tierList, data: { ...tierList.data, rows: [{ ...tierList.data.rows[0], technique: null }] } };
  server.use(http.get("/api/techniques", () => HttpResponse.json(onlyUnknown)));
  renderApp("/techniques");
  const card = await screen.findByRole("region", { name: "Trend" });
  expect(card).toHaveTextContent("No technique in the tier list for these filters.");
});
