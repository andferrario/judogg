import { toggleScoreValue } from "./scoreValues";

test("switching off one value of all three keeps the other two", () => {
  expect(toggleScoreValue([], "waza_ari")).toEqual(["ippon", "yuko"]);
});

test("switching the last values back on means all of them", () => {
  expect(toggleScoreValue(["ippon", "yuko"], "waza_ari")).toEqual([]);
});

test("the last value on cannot be switched off", () => {
  expect(toggleScoreValue(["yuko"], "yuko")).toBeNull();
});
