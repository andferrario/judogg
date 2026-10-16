import { screen, waitFor, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { scoresPage1, scoresPage2 } from "../../test/fixtures";
import { currentParams, lastNavigation, renderApp } from "../../test/render";
import { server } from "../../test/server";

const card = () => screen.findByRole("region", { name: "Scores" });

function recordScoreQueries() {
  const queries: Record<string, string>[] = [];
  server.use(
    http.get("/api/techniques/:code/scores", ({ request }) => {
      const query = Object.fromEntries(new URL(request.url).searchParams);
      queries.push(query);
      return HttpResponse.json(query.page === "2" ? scoresPage2 : scoresPage1);
    }),
  );
  return queries;
}

test("every score with its contest, both athletes, value, side, time and video links", async () => {
  renderApp("/techniques/uchi_mata?gender=m");
  const scores = await card();
  expect(scores).toHaveAttribute("id", "scores");
  expect(scores).toHaveTextContent("52 results");
  const [row] = within(scores).getAllByRole("row", { name: /Lapu ROSUGU/ });
  for (const text of ["2026-02-07", "Paris Grand Slam 2026", "+100 M", "Ippon", "Right", "3:00+"]) {
    expect(row).toHaveTextContent(text);
  }
  expect(within(row).getByRole("link", { name: "Bilo KAPIRE" })).toHaveAttribute("href", "/athletes/900576?gender=m");
  expect(within(row).getByRole("link", { name: "JudoBase ↗" })).toHaveAttribute(
    "href",
    "https://judobase.ijf.org/#/competition/contest/gs_fra2026_0001_m_p100_0017",
  );
  expect(within(row).getByRole("link", { name: "JudoTV ↗" })).toHaveAttribute("target", "_blank");
});

test("value chips filter the list, the last one stays on, and the list goes back to page 1", async () => {
  const queries = recordScoreQueries();
  const { user } = renderApp("/techniques/uchi_mata?v_page=2");
  const scores = await card();
  await user.click(within(scores).getByRole("button", { name: "Waza-ari" }));
  expect(currentParams()).toEqual({ v_score: "ippon,yuko" });
  expect(lastNavigation()).toBe("REPLACE");
  await user.click(within(scores).getByRole("button", { name: "Ippon" }));
  await user.click(within(scores).getByRole("button", { name: "Yuko" }));
  expect(currentParams()).toEqual({ v_score: "yuko" });
  expect(within(scores).getByRole("button", { name: "Yuko" })).toHaveAttribute("aria-pressed", "true");
  await waitFor(() => expect(queries.at(-1)).toMatchObject({ score_value: "yuko", page: "1", page_size: "10" }));
});

test("pagination asks for the next page", async () => {
  const queries = recordScoreQueries();
  const { user } = renderApp("/techniques/uchi_mata");
  const scores = await card();
  expect(within(scores).getByRole("navigation", { name: "Pages" })).toHaveTextContent("page 1 of 11");
  await user.click(within(scores).getByRole("button", { name: "Next →" }));
  expect(currentParams()).toEqual({ v_page: "2" });
  await waitFor(() => expect(queries.at(-1)).toMatchObject({ page: "2" }));
  expect(await within(scores).findByText("page 2 of 11")).toBeInTheDocument();
  await user.click(within(scores).getByRole("button", { name: "← Previous" }));
  expect(currentParams()).toEqual({});
});

test("no score with these values: an empty state", async () => {
  const none = { ...scoresPage1, data: { ...scoresPage1.data, rows: [], total: 0 } };
  server.use(http.get("/api/techniques/:code/scores", () => HttpResponse.json(none)));
  renderApp("/techniques/uchi_mata");
  expect(await card()).toHaveTextContent("No scores with these filters.");
});

test("the last value left on says why it does not switch off", async () => {
  const { user } = renderApp("/techniques/uchi_mata?v_score=yuko");
  const yuko = within(await card()).getByRole("button", { name: "Yuko" });
  expect(yuko).toHaveAttribute("aria-disabled", "true");
  expect(yuko).toHaveAttribute("data-tip", "At least one value stays on");
  await user.click(yuko);
  expect(currentParams()).toEqual({ v_score: "yuko" });
});
