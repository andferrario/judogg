import { screen, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { athleteSearch } from "../test/fixtures";
import { currentPath, renderApp } from "../test/render";
import { server } from "../test/server";

const suggestions = () => screen.getByRole("listbox", { name: "Suggestions" });
const searchBox = () => screen.findByRole("combobox", { name: "Search a technique, a shido reason or a judoka" });

function recordAthleteQueries(): string[] {
  const queries: string[] = [];
  server.use(
    http.get("/api/athletes", ({ request }) => {
      queries.push(new URL(request.url).searchParams.get("q") ?? "");
      return HttpResponse.json(athleteSearch);
    }),
  );
  return queries;
}

test("a technique typed without hyphens opens with Enter, keeping the filters", async () => {
  const { user } = renderApp("/techniques?gender=m&trend=x");
  const input = await searchBox();
  await user.type(input, "uchi mata");
  expect(within(suggestions()).getAllByRole("option")[0]).toHaveTextContent("Uchi-mata");
  await user.keyboard("{Enter}");
  expect(currentPath()).toBe("/techniques/uchi_mata?gender=m");
  expect(input).toHaveValue("");
});

test("a shido reason opens Penalties with its row highlighted", async () => {
  const { user } = renderApp("/techniques");
  await user.type(await searchBox(), "non comb");
  await user.click(within(suggestions()).getByRole("option", { name: /^Non-combativity/ }));
  expect(currentPath()).toBe("/penalties?reason=non_combativity");
});

test("judoka come from the API once the typing pauses, and open their page", async () => {
  const queries = recordAthleteQueries();
  const { user } = renderApp("/techniques?gender=m");
  await user.type(await searchBox(), "sadid");
  await user.click(await screen.findByRole("option", { name: "Tagi SADIDI AZE · -66 M" }));
  expect(currentPath()).toBe("/athletes/900323?gender=m");
  expect(queries).toEqual(["sadid"]);
});

test("one character does not ask the API", async () => {
  const queries = recordAthleteQueries();
  const { user } = renderApp("/techniques");
  await user.type(await searchBox(), "p");
  await new Promise((resolve) => setTimeout(resolve, 300));
  expect(queries).toEqual([]);
});

test("arrows move through the suggestions and Escape closes them", async () => {
  const { user } = renderApp("/techniques");
  const input = await searchBox();
  await user.type(input, "uchi mata");
  await user.keyboard("{ArrowDown}");
  const second = within(suggestions()).getByRole("option", { name: /^Uchi-mata-gaeshi/ });
  expect(second).toHaveAttribute("aria-selected", "true");
  expect(input).toHaveAttribute("aria-activedescendant", second.id);
  await user.keyboard("{Escape}");
  expect(input).toHaveAttribute("aria-expanded", "false");
});
