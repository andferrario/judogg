import { readSort, sortChange } from "./tierSort";

test("a new column sorts descending; the default share descending is not written", () => {
  expect(sortChange({ sort: "share", order: "desc" }, "n_scores")).toEqual({ sort: "n_scores", order: null });
  expect(sortChange({ sort: "n_scores", order: "desc" }, "share")).toEqual({ sort: null, order: null });
});

test("the active column toggles its order", () => {
  expect(sortChange({ sort: "n_scores", order: "desc" }, "n_scores")).toEqual({ sort: "n_scores", order: "asc" });
  expect(sortChange({ sort: "share", order: "desc" }, "share")).toEqual({ sort: null, order: "asc" });
  expect(sortChange({ sort: "share", order: "asc" }, "share")).toEqual({ sort: null, order: null });
});

test("the URL is read with the defaults", () => {
  expect(readSort(new URLSearchParams(""))).toEqual({ sort: "share", order: "desc" });
  expect(readSort(new URLSearchParams("sort=pct_yuko&order=asc"))).toEqual({ sort: "pct_yuko", order: "asc" });
});
