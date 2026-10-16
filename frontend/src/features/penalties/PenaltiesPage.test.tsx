import { screen, within } from "@testing-library/react";
import { renderApp } from "../../test/render";

test("the KPIs", async () => {
  renderApp("/penalties");
  const kpis = await screen.findByLabelText("Key figures");
  for (const text of ["910", "967 penalties in total", "1.77", "546 contests fought", "10.3%", "contests decided by the 3rd shido"]) {
    expect(kpis).toHaveTextContent(text);
  }
});

test("reasons: share, count and how often each one decided the contest", async () => {
  renderApp("/penalties");
  const card = await screen.findByRole("region", { name: "Shido reasons" });
  const row = within(card).getByRole("row", { name: /^Non-combativity/ });
  for (const text of ["Passivity", "49.2%", "476", "37", "8%"]) expect(row).toHaveTextContent(text);
  expect(within(card).getByRole("row", { name: /^Squeeze head with legs/ })).toHaveAttribute(
    "data-sample",
    "insufficient",
  );
});

test("the reason chosen in the search is highlighted", async () => {
  renderApp("/penalties?reason=false_attack");
  const card = await screen.findByRole("region", { name: "Shido reasons" });
  expect(within(card).getByRole("row", { name: /^False-attack/ })).toHaveAttribute("data-selected");
  expect(within(card).getByRole("row", { name: /^Non-combativity/ })).not.toHaveAttribute("data-selected");
});

test("an unknown reason highlights nothing", async () => {
  renderApp("/penalties?reason=nope");
  const card = await screen.findByRole("region", { name: "Shido reasons" });
  expect(card.querySelectorAll("tr[data-selected]")).toHaveLength(0);
});
