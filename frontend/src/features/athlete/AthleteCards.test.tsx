import { screen, waitFor, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { athlete } from "../../test/fixtures";
import { currentPath, renderApp } from "../../test/render";
import { server } from "../../test/server";

test("techniques: share of their scores, breakdown and side, the Unknown row last", async () => {
  renderApp("/athletes/900323");
  const card = await screen.findByRole("region", { name: "Techniques" });
  const row = within(card).getByRole("row", { name: /^Kata-guruma/ });
  for (const text of ["Te-waza", "2", "20%", "100%"]) expect(row).toHaveTextContent(text);
  const rows = within(card).getAllByRole("row");
  expect(rows.at(-1)).toHaveTextContent("Unknown technique");
  expect(rows.at(-1)).toHaveTextContent("no technique tag");
});

test("videos: one group per technique, the first one open", async () => {
  renderApp("/athletes/900323");
  const card = await screen.findByRole("region", { name: "Videos by technique" });
  expect(card).toHaveAttribute("id", "videos");
  const groups = card.querySelectorAll("details");
  expect(groups).toHaveLength(8);
  expect(groups[0]).toHaveAttribute("open");
  expect(groups[1]).not.toHaveAttribute("open");
  expect(groups[0].querySelector("summary")).toHaveTextContent("Kata-guruma 2 scores");
  const row = within(groups[0] as HTMLElement).getAllByRole("row")[1];
  for (const text of ["2025-10-17", "Guadalajara Grand Prix 2025", "-66 M", "Waza-ari", "Left", "GS"]) {
    expect(row).toHaveTextContent(text);
  }
  expect(within(row).getByRole("link", { name: "Supo DUMUDO" })).toHaveAttribute("href", "/athletes/900135");
  expect(within(row).getByRole("link", { name: "JudoTV ↗" })).toHaveAttribute("target", "_blank");
});

test("the videos button of a technique opens its group", async () => {
  const { user } = renderApp("/athletes/900323");
  const card = await screen.findByRole("region", { name: "Techniques" });
  await user.click(within(card).getByRole("button", { name: "1 video of Tai-otoshi" }));
  expect(document.getElementById("videos-tai_otoshi")).toHaveAttribute("open");
});

test("an athlete with one technique: its group is open", async () => {
  const one = { ...athlete, data: { ...athlete.data, score_groups: athlete.data.score_groups.slice(0, 1) } };
  server.use(http.get("/api/athletes/:id", () => HttpResponse.json(one)));
  renderApp("/athletes/900323");
  const card = await screen.findByRole("region", { name: "Videos by technique" });
  expect(card.querySelectorAll("details")).toHaveLength(1);
  expect(card.querySelector("details")).toHaveAttribute("open");
});

test("another athlete opens with their own first video group open", async () => {
  server.use(
    http.get("/api/athletes/:id", ({ params }) =>
      HttpResponse.json({
        ...athlete,
        data: { ...athlete.data, athlete: { ...athlete.data.athlete, id: Number(params.id) } },
      }),
    ),
  );
  const { user } = renderApp("/athletes/900323");
  const techniques = await screen.findByRole("region", { name: "Techniques" });
  await user.click(within(techniques).getByRole("button", { name: "1 video of Tai-otoshi" }));
  const videos = screen.getByRole("region", { name: "Videos by technique" });
  (videos.querySelector("details") as HTMLDetailsElement).open = false;
  await user.click(within(screen.getByRole("region", { name: "Similar athletes" })).getByRole("link", { name: /^Fomi DUGUMA/ }));
  await waitFor(() => expect(currentPath()).toBe("/athletes/900049"));
  const groups = screen.getByRole("region", { name: "Videos by technique" }).querySelectorAll("details");
  await waitFor(() => expect(groups[0]).toHaveAttribute("open"));
  expect(document.getElementById("videos-tai_otoshi")).not.toHaveAttribute("open");
});
