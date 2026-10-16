import { savedFilters, saveFilters, searchWithSavedFilters } from "./persistence";

test("the saved filters are restored when the URL has none, page parameters kept", () => {
  saveFilters({ gender: "m", weight: "m-73,m-81" });
  expect(searchWithSavedFilters("?trend=uchi_mata")).toBe("?trend=uchi_mata&gender=m&weight=m-73,m-81");
});

test("filters in the URL win over the saved ones", () => {
  saveFilters({ gender: "m" });
  expect(searchWithSavedFilters("?gender=f")).toBeNull();
});

test("nothing saved, nothing restored", () => {
  expect(searchWithSavedFilters("")).toBeNull();
});

test("unknown keys, wrong types and malformed storage are ignored", () => {
  localStorage.setItem("judogg-filters", JSON.stringify({ gender: "m", trend: "x", weight: 3 }));
  expect(savedFilters()).toEqual({ gender: "m" });
  localStorage.setItem("judogg-filters", "{not json");
  expect(savedFilters()).toEqual({});
  localStorage.setItem("judogg-filters", "null");
  expect(savedFilters()).toEqual({});
});

test("an unavailable storage does not break the app", () => {
  vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
    throw new DOMException("full", "QuotaExceededError");
  });
  vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
    throw new DOMException("blocked", "SecurityError");
  });
  expect(() => saveFilters({ gender: "m" })).not.toThrow();
  expect(savedFilters()).toEqual({});
  expect(searchWithSavedFilters("")).toBeNull();
});
