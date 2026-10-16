import {
  athleteName,
  DOMAIN_LABEL,
  END_LABEL,
  formatCount,
  formatDecimal,
  formatDuration,
  formatPercent,
  formatTimeBin,
  SIDE_LABEL,
  VALUE_LABEL,
  weightLabel,
} from "./format";

test.each([
  [0, "0"],
  [1234, "1,234"],
  [1234567, "1,234,567"],
  [null, "–"],
])("formatCount(%s) is %s", (value, text) => {
  expect(formatCount(value)).toBe(text);
});

test("percentages have no decimals unless asked", () => {
  expect(formatPercent(0.2436)).toBe("24%");
  expect(formatPercent(0.0987, 1)).toBe("9.9%");
  expect(formatPercent(1)).toBe("100%");
  expect(formatPercent(null)).toBe("–");
});

test("decimals default to two", () => {
  expect(formatDecimal(1.3512)).toBe("1.35");
  expect(formatDecimal(0.87, 1)).toBe("0.9");
  expect(formatDecimal(null)).toBe("–");
});

test.each([
  [5, "0:05"],
  [75, "1:15"],
  [150.6, "2:31"],
  [null, "–"],
])("formatDuration(%s) is %s", (seconds, text) => {
  expect(formatDuration(seconds)).toBe(text);
});

test("weight labels carry the gender initial", () => {
  expect(weightLabel({ code: "m-73", gender: "m", label: "-73" })).toBe("-73 M");
  expect(weightLabel({ code: "f+78", gender: "f", label: "+78" })).toBe("+78 W");
});

test("athlete names are the given name, then the family name", () => {
  expect(athleteName({ id: 900323, given_name: "Tagi", family_name: "SADIDI", country_code: "AZE" })).toBe(
    "Tagi SADIDI",
  );
});

test("the label maps name every API value", () => {
  expect(VALUE_LABEL).toEqual({ ippon: "Ippon", waza_ari: "Waza-ari", yuko: "Yuko" });
  expect(END_LABEL.waza_ari_awasete).toBe("Waza-ari awasete ippon");
  expect(END_LABEL.hansoku_shido).toBe("Hansoku-make (3rd shido)");
  expect(DOMAIN_LABEL).toEqual({ standing: "Standing", ground: "Ground", unknown: "Unknown" });
});

test("a time bin is the start of its 30-second block, or GS", () => {
  expect(formatTimeBin(0, false)).toBe("0:00+");
  expect(formatTimeBin(6, false)).toBe("3:00+");
  expect(formatTimeBin(8, true)).toBe("GS");
});

test("sides are capitalised", () => {
  expect(SIDE_LABEL).toEqual({ left: "Left", right: "Right", unknown: "Unknown" });
});
