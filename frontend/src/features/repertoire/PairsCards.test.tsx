import { screen, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { pairsNone } from "../../test/fixtures";
import { currentParams, lastNavigation, renderApp } from "../../test/render";
import { server } from "../../test/server";

test("frequent pairs: support, confidence and lift; a pair opens in the cards above", async () => {
  const { user } = renderApp("/repertoire?gender=m");
  const card = await screen.findByRole("region", { name: "Frequent pairs" });
  const row = within(card).getByRole("row", { name: /^O-soto-gari Ko-soto-gari/ });
  for (const text of ["6", "5.4%", "38%", "2.91"]) expect(row).toHaveTextContent(text);
  expect(row).toHaveAttribute("data-sample", "small");
  await user.click(within(row).getByRole("link", { name: "O-soto-gari" }));
  expect(currentParams()).toEqual({ gender: "m", technique: "o_soto_gari", with: "ko_soto_gari" });
  expect(lastNavigation()).toBe("REPLACE");
});

test("without frequent pairs: the threshold in the empty state", async () => {
  server.use(http.get("/api/repertoire/pairs", () => HttpResponse.json(pairsNone)));
  renderApp("/repertoire");
  const card = await screen.findByRole("region", { name: "Frequent pairs" });
  expect(card).toHaveTextContent("No pair with at least 5 athletes in common.");
});

test("the lift matrix: a cell per pair with its lift, opening the pair", async () => {
  renderApp("/repertoire");
  const card = await screen.findByRole("region", { name: "Lift matrix" });
  const cell = within(card).getByRole("link", { name: "Seoi-nage + O-uchi-gari: lift 0.89 · 9 athletes with both" });
  expect(cell).toHaveTextContent("0.9");
  expect(cell).toHaveAttribute("href", "/repertoire?technique=seoi_nage&with=o_uchi_gari");
  expect(within(card).getByText("below 1")).toBeInTheDocument();
});

test("pairs with too few athletes show a neutral dot", async () => {
  server.use(http.get("/api/repertoire/pairs", () => HttpResponse.json(pairsNone)));
  renderApp("/repertoire");
  const card = await screen.findByRole("region", { name: "Lift matrix" });
  const cells = within(card).getAllByRole("link");
  expect(cells).toHaveLength(90);
  expect(new Set(cells.map((cell) => cell.textContent))).toEqual(new Set(["·"]));
});
