import { athleteSearch, meta } from "../test/fixtures";
import { athleteOptions, catalogueOptions, normalise } from "./searchOptions";

test("case, hyphens and accents do not matter", () => {
  expect(normalise("  Uchi-Matá ")).toBe("uchi mata");
});

test("techniques match without their hyphens", () => {
  expect(catalogueOptions(meta, "uchi mata").map((option) => option.label)).toEqual([
    "Uchi-mata",
    "Uchi-mata-gaeshi",
    "Uchi-mata-makikomi",
    "Uchi-mata-sukashi",
  ]);
  expect(catalogueOptions(meta, "uchi mata")[0]).toEqual({
    id: "technique-uchi_mata",
    label: "Uchi-mata",
    detail: "Technique · Ashi-waza",
    pathname: "/techniques/uchi_mata",
  });
});

test("a shido reason opens Penalties on its row", () => {
  expect(catalogueOptions(meta, "non comb")).toEqual([
    {
      id: "reason-non_combativity",
      label: "Non-combativity",
      detail: "Shido reason · Passivity",
      pathname: "/penalties",
      extra: { reason: "non_combativity" },
    },
  ]);
});

test("blank or symbol-only text matches nothing and does not throw", () => {
  expect(catalogueOptions(meta, "   ")).toEqual([]);
  expect(catalogueOptions(meta, "(")).toEqual([]);
});

test("judoka options carry country and categories", () => {
  expect(athleteOptions(athleteSearch.rows)).toEqual([
    { id: "athlete-900323", label: "Tagi SADIDI", detail: "AZE · -66 M", pathname: "/athletes/900323" },
  ]);
});
