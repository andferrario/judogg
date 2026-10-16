import type { ApiFilters } from "../api/types";
import { meta, overview } from "../test/fixtures";
import {
  changeFilters,
  changeParams,
  countChanged,
  filterSearch,
  filterSummary,
  genderChange,
  readFilters,
  resetFilters,
  rulesetToggle,
  sideChange,
  toSearch,
  yearRange,
  type FilterChange,
} from "./filters";

const params = (search: string) => new URLSearchParams(search);
const defaults = meta.defaults;

describe("readFilters", () => {
  test("keeps only the filter parameters that have a value", () => {
    expect(readFilters(params("gender=m&weight=&trend=uchi_mata&ruleset=2025,2018"))).toEqual({
      gender: "m",
      ruleset: "2025,2018",
    });
  });
});

describe("filterSearch", () => {
  test("keeps the filters, drops the page parameters, adds the extras", () => {
    expect(filterSearch(params("gender=m&weight=m-73,m-81&trend=x&v_page=2"), { reason: "non_combativity" })).toBe(
      "?gender=m&weight=m-73,m-81&reason=non_combativity",
    );
  });

  test("is empty without filters", () => {
    expect(filterSearch(params("trend=x"))).toBe("");
  });
});

describe("changeFilters", () => {
  test("sets a filter and restarts the scores list", () => {
    expect(toSearch(changeFilters(params("trend=x&v_page=3"), { country: "JPN" }, defaults))).toBe(
      "?trend=x&country=JPN",
    );
  });

  test("an empty value removes the filter", () => {
    expect(toSearch(changeFilters(params("country=JPN"), { country: "" }, defaults))).toBe("");
  });

  test.each([
    ["gender", "all"],
    ["count_by", "event"],
    ["min_scores_athlete", "5"],
    ["min_scores_technique", "2"],
    ["ruleset", "2025"],
  ])("never writes the default %s", (key, value) => {
    const change = { [key]: value } as FilterChange;
    expect(toSearch(changeFilters(params(`${key}=x`), change, defaults))).toBe("");
  });

  test("writes values that are not the default", () => {
    expect(toSearch(changeFilters(params(""), { gender: "m", ruleset: "2018,2025" }, defaults))).toBe(
      "?gender=m&ruleset=2018,2025",
    );
  });
});

describe("resetFilters", () => {
  test("removes every filter and the scores page, keeps the other page parameters", () => {
    expect(toSearch(resetFilters(params("gender=m&weight=m-73&trend=x&v_page=2")))).toBe("?trend=x");
  });
});

test("countChanged counts the filters in the URL", () => {
  expect(countChanged(params("gender=m&weight=m-73&trend=x"))).toBe(2);
});

describe("genderChange", () => {
  test("drops the weights of the other gender", () => {
    expect(genderChange(params("weight=m-73,f-57"), "f", meta.weights)).toEqual({ gender: "f", weight: "f-57" });
  });

  test("keeps every weight for both genders", () => {
    expect(genderChange(params("weight=m-73,f-57"), "all", meta.weights)).toEqual({
      gender: "all",
      weight: "m-73,f-57",
    });
  });
});

describe("rulesetToggle", () => {
  test("adds to the rulesets on screen, the default included, and clears the years", () => {
    expect(rulesetToggle(params("year_from=2025"), "2018", defaults)).toEqual({
      ruleset: "2025,2018",
      year_from: null,
      year_to: null,
    });
  });

  test("removes a selected ruleset", () => {
    expect(rulesetToggle(params("ruleset=2025,2018"), "2025", defaults)).toMatchObject({ ruleset: "2018" });
  });
});

describe("sideChange", () => {
  test("unchecking one side lists the others", () => {
    expect(sideChange(params(""), "unknown", false)).toBe("left,right");
  });

  test("checking the last side back removes the filter", () => {
    expect(sideChange(params("side=left,right"), "unknown", true)).toBeNull();
  });

  test("unchecking the only side left removes the filter", () => {
    expect(sideChange(params("side=left"), "left", false)).toBeNull();
  });
});

describe("yearRange", () => {
  test("offers the years with contests of the selected rulesets", () => {
    expect(yearRange(params(""), meta)).toEqual({ years: [2025, 2026], from: 2025, to: 2026 });
  });

  test("reads the chosen years", () => {
    expect(yearRange(params("year_from=2026"), meta)).toEqual({ years: [2025, 2026], from: 2026, to: 2026 });
  });

  test("rulesets without contests offer no year", () => {
    expect(yearRange(params("ruleset=2018"), meta)).toEqual({ years: [], from: undefined, to: undefined });
  });

  test("an unknown ruleset or a malformed year does not throw", () => {
    expect(yearRange(params("ruleset=9999&year_from=abc"), meta)).toEqual({
      years: [],
      from: undefined,
      to: undefined,
    });
  });
});

describe("filterSummary", () => {
  test("describes the filters applied by default", () => {
    expect(filterSummary(overview.filters, meta)).toBe("Men and women · all weights · rules 2025– · 2025–2027");
  });

  test("names every filter that is not 'all'", () => {
    const filters: ApiFilters = {
      ...overview.filters,
      gender: "m",
      weight: ["m-66", "m-73"],
      year_from: 2026,
      year_to: 2026,
      country: ["JPN", "FRA"],
      domain: ["standing"],
      side: ["left", "right"],
    };
    expect(filterSummary(filters, meta)).toBe(
      "Men · -66, -73 kg · rules 2025– · 2026 · JPN, FRA · Standing · side left/right",
    );
  });
});

test("changeParams sets page parameters and removes the empty ones, filters untouched", () => {
  expect(toSearch(changeParams(params("gender=m&v_page=3&sort=n_scores"), { sort: null, all: "1", v_page: "" }))).toBe(
    "?gender=m&all=1",
  );
});
