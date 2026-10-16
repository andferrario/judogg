import { screen, waitFor, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { tierList, tierListByAthlete } from "../../test/fixtures";
import { currentParams, lastNavigation, renderApp } from "../../test/render";
import { server } from "../../test/server";

const card = () => screen.findByRole("region", { name: "Top techniques" });

function recordTierQueries(response = tierList) {
  const queries: Record<string, string>[] = [];
  server.use(
    http.get("/api/techniques", ({ request }) => {
      queries.push(Object.fromEntries(new URL(request.url).searchParams));
      return HttpResponse.json(response);
    }),
  );
  return queries;
}

test("each row shows the technique, its share, counts, breakdown, awasete and side", async () => {
  renderApp("/techniques?gender=m");
  const row = within(await card()).getByRole("row", { name: /^Seoi-nage/ });
  expect(row).toHaveTextContent("Te-waza · Standing");
  for (const text of ["9.9%", "75", "19%", "36%", "45%", "61%", "39%"]) expect(row).toHaveTextContent(text);
  expect(within(row).getByRole("link", { name: "Seoi-nage" })).toHaveAttribute("href", "/techniques/seoi_nage?gender=m");
});

test("rows below the sample threshold are greyed out, not hidden", async () => {
  renderApp("/techniques");
  expect(within(await card()).getByRole("row", { name: /^Koshi-guruma/ })).toHaveAttribute(
    "data-sample",
    "insufficient",
  );
});

test("by event: share of scores; by athlete: share of athletes, and the Unknown row is plain text", async () => {
  server.use(http.get("/api/techniques", () => HttpResponse.json(tierListByAthlete)));
  renderApp("/techniques?count_by=athlete&all=1");
  const tier = await card();
  expect(within(tier).getByRole("button", { name: "About Share (by athlete)" })).toBeInTheDocument();
  expect(within(tier).getByRole("columnheader", { name: "Share of athletes" })).toBeInTheDocument();
  const unknown = within(tier).getByRole("row", { name: /^Unknown technique/ });
  expect(unknown).toHaveTextContent("no technique tag");
  expect(within(unknown).queryByRole("link")).not.toBeInTheDocument();
});

test("the list asks for 15 rows, all of them after Show all, and back", async () => {
  const queries = recordTierQueries();
  const { user } = renderApp("/techniques");
  await user.click(within(await card()).getByRole("button", { name: "Show all (59)" }));
  expect(currentParams()).toEqual({ all: "1" });
  expect(lastNavigation()).toBe("REPLACE");
  await waitFor(() => expect(queries.at(-1)).toMatchObject({ limit: "200", sort: "share", order: "desc" }));
  expect(queries[0]).toMatchObject({ limit: "15" });
  await user.click(screen.getByRole("button", { name: "Show top 15" }));
  expect(currentParams()).toEqual({});
});

test("a header click sorts descending, a second click ascending, the share column goes back to the default", async () => {
  const queries = recordTierQueries();
  const { user } = renderApp("/techniques");
  const tier = await card();
  await user.click(within(tier).getByRole("button", { name: "Scores" }));
  expect(currentParams()).toEqual({ sort: "n_scores" });
  expect(within(tier).getByRole("columnheader", { name: "Scores" })).toHaveAttribute("aria-sort", "descending");
  await user.click(within(tier).getByRole("button", { name: "Scores" }));
  expect(currentParams()).toEqual({ sort: "n_scores", order: "asc" });
  await waitFor(() => expect(queries.at(-1)).toMatchObject({ sort: "n_scores", order: "asc" }));
  await user.click(within(tier).getByRole("button", { name: "Share of scores" }));
  expect(currentParams()).toEqual({});
});
