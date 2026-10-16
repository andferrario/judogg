import { screen, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { noScoresDetail } from "../../test/fixtures";
import { currentPath, lastNavigation, renderApp } from "../../test/render";
import { server } from "../../test/server";

test("the header names the technique, its group and type, then the filters", async () => {
  renderApp("/techniques/uchi_mata?gender=m");
  expect(await screen.findByRole("heading", { level: 1, name: "Uchi-mata" })).toHaveAttribute("data-big");
  expect(
    await screen.findByText("Ashi-waza · Standing · Men and women · all weights · rules 2025– · 2025–2027"),
  ).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "← Techniques" })).toHaveAttribute("href", "/techniques?gender=m");
});

test("Change technique opens the other technique with the filters, in a new history entry", async () => {
  const { user } = renderApp("/techniques/uchi_mata?gender=m&v_page=2");
  await user.selectOptions(await screen.findByLabelText("Change technique"), "seoi_nage");
  expect(currentPath()).toBe("/techniques/seoi_nage?gender=m");
  expect(lastNavigation()).toBe("PUSH");
});

test("the KPIs", async () => {
  renderApp("/techniques/uchi_mata");
  const kpis = await screen.findByLabelText("Key figures");
  for (const text of [
    "52",
    "#3 of 58 techniques",
    "21% · 35% · 44%",
    "overall ippon 28% · awasete 1",
    "60%",
    "of known side · unknown 4%",
    "42",
    "8%",
    "of its scores came in golden score · overall 13%",
  ]) {
    expect(kpis).toHaveTextContent(text);
  }
  expect(within(kpis).getByRole("button", { name: "About Ippon / waza-ari / yuko breakdown" })).toBeInTheDocument();
});

test("no score for the filters: an empty state and nothing else", async () => {
  server.use(http.get("/api/techniques/:code", () => HttpResponse.json(noScoresDetail)));
  renderApp("/techniques/uchi_mata?ruleset=2018");
  expect(
    await screen.findByText("No scores with this technique for the current filters. Widen the filters."),
  ).toBeInTheDocument();
  expect(screen.queryByLabelText("Key figures")).not.toBeInTheDocument();
});

test("ground techniques carry the hold-down notice, standing ones do not", async () => {
  renderApp("/techniques/yoko_shiho_gatame");
  expect(await screen.findByRole("note")).toHaveTextContent("For osaekomi techniques");
});

test("a standing technique has no hold-down notice", async () => {
  renderApp("/techniques/uchi_mata");
  await screen.findByLabelText("Key figures");
  expect(screen.queryByRole("note")).not.toBeInTheDocument();
});

test("an unknown technique shows Not found, the header still readable", async () => {
  renderApp("/techniques/flying_armbar?gender=m");
  expect(await screen.findByRole("alert")).toHaveTextContent("Not found.");
  expect(screen.getByRole("heading", { level: 1, name: "flying_armbar" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Go to Techniques" })).toHaveAttribute("href", "/techniques?gender=m");
});
