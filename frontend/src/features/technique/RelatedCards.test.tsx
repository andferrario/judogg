import { screen, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { counters, repertoire, uchiMataDetail } from "../../test/fixtures";
import { renderApp } from "../../test/render";
import { server } from "../../test/server";

test("top athletes link to their judoka page and to JudoBase", async () => {
  renderApp("/techniques/uchi_mata?gender=m");
  const card = await screen.findByRole("region", { name: "Top athletes" });
  const row = within(card).getByRole("row", { name: /^Bapu ZUBUNI/ });
  expect(within(row).getByRole("link", { name: "Bapu ZUBUNI" })).toHaveAttribute(
    "href",
    "/athletes/900263?gender=m",
  );
  expect(row).toHaveTextContent("57% of 7");
  const profile = within(row).getByRole("link", { name: "JudoBase ↗" });
  expect(profile).toHaveAttribute("href", "https://judobase.ijf.org/#/competitor/profile/900263");
  expect(profile).toHaveAttribute("target", "_blank");
});

test("repertoire: the cohort, the companions and a link to the Repertoire page", async () => {
  renderApp("/techniques/uchi_mata?gender=m");
  const card = await screen.findByRole("region", { name: "Repertoire" });
  expect(card).toHaveTextContent("3 of 45 eligible athletes have Uchi-mata in their repertoire.");
  expect(within(card).getByRole("link", { name: "Ko-soto-gake" })).toBeInTheDocument();
  expect(within(card).getByText("insufficient · n=3")).toBeInTheDocument();
  expect(within(card).getByRole("link", { name: "Open in Repertoire" })).toHaveAttribute(
    "href",
    "/repertoire?gender=m&technique=uchi_mata",
  );
});

test("repertoire without companions: an empty state with the threshold", async () => {
  const empty = { ...repertoire, data: { ...repertoire.data, companions: [] } };
  server.use(http.get("/api/repertoire", () => HttpResponse.json(empty)));
  renderApp("/techniques/uchi_mata");
  const card = await screen.findByRole("region", { name: "Repertoire" });
  expect(card).toHaveTextContent(
    "No eligible athlete scored at least 2 times with Uchi-mata. Widen the filters or lower the thresholds.",
  );
});

test("counter: the specialists are named and linked, the Unknown row is plain text", async () => {
  renderApp("/techniques/uchi_mata");
  const card = await screen.findByRole("region", { name: "Counter" });
  expect(card).toHaveTextContent("2 specialists (main technique, ≥ 40% of their scores) conceded 2 scores:");
  expect(within(card).getByRole("link", { name: "Gefe BOPEDU" })).toHaveAttribute("href", "/athletes/900498");
  const unknown = within(card).getByRole("row", { name: /^Unknown technique/ });
  expect(within(unknown).queryByRole("link")).not.toBeInTheDocument();
  expect(within(card).getByRole("row", { name: /^Sumi-gaeshi/ })).toHaveTextContent("10.25");
  expect(card).toHaveTextContent("A lift above 1: it scores against them more often than usual.");
});

test("counter: specialists who conceded nothing are named, not denied", async () => {
  const none = { ...counters, data: { ...counters.data, conceded: { ...counters.data.conceded, n: 0 }, rows: [] } };
  server.use(http.get("/api/counters", () => HttpResponse.json(none)));
  renderApp("/techniques/uchi_mata");
  const card = await screen.findByRole("region", { name: "Counter" });
  expect(card).toHaveTextContent("2 specialists (main technique, ≥ 40% of their scores) conceded 0 scores:");
  expect(within(card).getByRole("link", { name: "Gefe BOPEDU" })).toBeInTheDocument();
  expect(card).toHaveTextContent("They conceded no score with these filters.");
});

test("counter without specialists: an empty state", async () => {
  const specialists = { ...counters.data.specialists, n: 0, athletes: [] };
  const none = { ...counters, data: { ...counters.data, specialists, rows: [] } };
  server.use(http.get("/api/counters", () => HttpResponse.json(none)));
  renderApp("/techniques/uchi_mata");
  const card = await screen.findByRole("region", { name: "Counter" });
  expect(card).toHaveTextContent("No specialist of Uchi-mata with these filters.");
});

test("top athletes: an empty state when there is none", async () => {
  const detail = { ...uchiMataDetail, data: { ...uchiMataDetail.data, top_athletes: [] } };
  server.use(http.get("/api/techniques/:code", () => HttpResponse.json(detail)));
  renderApp("/techniques/uchi_mata");
  expect(await screen.findByRole("region", { name: "Top athletes" })).toHaveTextContent(
    "No athlete with these filters.",
  );
});
