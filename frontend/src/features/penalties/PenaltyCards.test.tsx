import { screen, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { penalties } from "../../test/fixtures";
import { server } from "../../test/server";
import { renderApp } from "../../test/render";

test("by group: one split bar with the shares in its legend", async () => {
  renderApp("/penalties");
  const card = await screen.findByRole("region", { name: "By group" });
  for (const text of ["Passivity 75%", "Grip 21%", "Infractions 4%", "Other 0%"]) {
    expect(within(card).getByText(text)).toBeInTheDocument();
  }
});

test("when shidos happen: the nine blocks, golden score apart", async () => {
  renderApp("/penalties");
  const card = await screen.findByRole("region", { name: "When shidos happen" });
  expect(within(card).getByRole("img", { name: "Penalties per 30-second block" })).toBeInTheDocument();
  expect(card).toHaveTextContent("Golden score: 103 penalties");
});

test("by weight: shidos per contest and hansoku-make", async () => {
  renderApp("/penalties");
  const card = await screen.findByRole("region", { name: "By weight" });
  const row = within(card).getByRole("row", { name: /^-60 M/ });
  for (const text of ["42", "1.88", "4.8%"]) expect(row).toHaveTextContent(text);
});

test("1st, 2nd, 3rd shido: the main reasons of each", async () => {
  renderApp("/penalties");
  const card = await screen.findByRole("region", { name: "1st, 2nd, 3rd shido" });
  expect(within(card).getByRole("heading", { name: "1st shido · 628" })).toBeInTheDocument();
  expect(within(card).getByRole("heading", { name: "3rd shido · 57" })).toBeInTheDocument();
  const [first] = within(card).getAllByRole("listitem");
  expect(first).toHaveTextContent("Non-combativity");
  expect(first).toHaveTextContent("49%");
});

test("filters without penalties: every card says so instead of staying empty", async () => {
  const empty = {
    ...penalties,
    data: {
      ...penalties.data,
      reasons: [],
      by_group: [],
      by_number: penalties.data.by_number.map((number) => ({ ...number, n: 0, reasons: [] })),
    },
  };
  server.use(http.get("/api/penalties", () => HttpResponse.json(empty)));
  renderApp("/penalties?gender=m&country=ANG");
  expect(await screen.findByRole("region", { name: "Shido reasons" })).toHaveTextContent("No penalty with these filters.");
  expect(screen.getByRole("region", { name: "By group" })).toHaveTextContent("No penalty with these filters.");
  expect(screen.getByRole("region", { name: "1st, 2nd, 3rd shido" })).toHaveTextContent("none");
});
