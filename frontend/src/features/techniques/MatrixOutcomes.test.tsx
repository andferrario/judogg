import { screen, within } from "@testing-library/react";
import { renderApp } from "../../test/render";

test("weight × technique: each cell opens the technique on that weight, keeping the other filters", async () => {
  renderApp("/techniques?ruleset=2025,2018&trend=x");
  const card = await screen.findByRole("region", { name: "Weight × technique" });
  const cell = within(card).getByRole("link", { name: "-60 M · Seoi-nage: 13.6% (8 of 59 scores)" });
  expect(cell).toHaveTextContent("14%");
  expect(cell).toHaveAttribute("href", "/techniques/seoi_nage?ruleset=2025,2018&weight=m-60&gender=m");
});

test("outcomes: one row per weight and an All row, walkovers apart", async () => {
  renderApp("/techniques");
  const card = await screen.findByRole("region", { name: "Golden score & outcomes" });
  const first = within(card).getByRole("row", { name: /^-60 M/ });
  for (const text of ["40%", "42", "38%", "5%", "1.88", "3:56", "0 · 0"]) expect(first).toHaveTextContent(text);
  const all = within(card).getByRole("row", { name: /^All/ });
  for (const text of ["24%", "546", "46%", "10%", "1.77", "3:38", "8 · 2"]) expect(all).toHaveTextContent(text);
  expect(card).toHaveTextContent("walkovers (fusen-gachi) and withdrawals (kiken-gachi) are counted apart");
});
