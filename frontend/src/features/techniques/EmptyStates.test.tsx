import { screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { outcomes, tierList, weightMatrix } from "../../test/fixtures";
import { renderApp } from "../../test/render";
import { server } from "../../test/server";

const NO_SCORE = "No score with these filters. Widen the filters.";

test("the tier list says so when no technique scores", async () => {
  server.use(
    http.get("/api/techniques", () =>
      HttpResponse.json({ ...tierList, data: { ...tierList.data, rows: [], total_rows: 0 } }),
    ),
  );
  renderApp("/techniques");
  expect(await screen.findByRole("region", { name: "Top techniques" })).toHaveTextContent(NO_SCORE);
});

test("weight × technique says so when there is no cell", async () => {
  server.use(
    http.get("/api/techniques/by-weight", () =>
      HttpResponse.json({ ...weightMatrix, data: { techniques: [], rows: [] } }),
    ),
  );
  renderApp("/techniques");
  expect(await screen.findByRole("region", { name: "Weight × technique" })).toHaveTextContent(NO_SCORE);
});

test("outcomes say so when no contest was fought", async () => {
  const total = { ...outcomes.data.total, played: 0, walkovers: { fusen_gachi: 0, kiken_gachi: 0 } };
  server.use(http.get("/api/outcomes", () => HttpResponse.json({ ...outcomes, data: { rows: [], total } })));
  renderApp("/techniques");
  expect(await screen.findByRole("region", { name: "Golden score & outcomes" })).toHaveTextContent(
    "No contest with these filters. Widen the filters.",
  );
});

test("outcomes with walkovers only keep the table: the walkovers are data", async () => {
  const total = { ...outcomes.data.total, played: 0, walkovers: { fusen_gachi: 1, kiken_gachi: 0 } };
  const row = { ...outcomes.data.rows[0], played: 0, walkovers: { fusen_gachi: 1, kiken_gachi: 0 } };
  server.use(http.get("/api/outcomes", () => HttpResponse.json({ ...outcomes, data: { rows: [row], total } })));
  renderApp("/techniques");
  const card = await screen.findByRole("region", { name: "Golden score & outcomes" });
  expect(card).not.toHaveTextContent("No contest with these filters.");
  expect(card).toHaveTextContent("1 · 0");
});
