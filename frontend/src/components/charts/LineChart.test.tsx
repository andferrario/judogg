import { screen } from "@testing-library/react";
import { renderWithRouter } from "../../test/render";
import { LineChart, niceMax } from "./LineChart";

const points = [
  { year: 2024, n: 4, total: 80, share: 0.05 },
  { year: 2025, n: 2, total: 42, share: 0.0476 },
  { year: 2026, n: 50, total: 714, share: 0.07 },
];

test("the chart is an image whose values are also readable as text", () => {
  renderWithRouter(<LineChart points={points} rulesetChanges={[]} label="Share of scores per year" />);
  expect(screen.getByRole("img", { name: "Share of scores per year" })).toBeInTheDocument();
  const values = screen.getByRole("list", { name: "Share of scores per year: values" });
  expect(values).toHaveTextContent("2025: 4.8% (2 of 42)");
  expect(values).toHaveTextContent("2026: 7.0% (50 of 714)");
});

test("each year has a hover area with its tooltip, and the y axis is labelled in percent", () => {
  const { container } = renderWithRouter(<LineChart points={points} rulesetChanges={[]} label="Trend" />);
  expect(container.querySelector("[data-tip='2024: 5.0% (4 of 80)']")).not.toBeNull();
  expect([...container.querySelectorAll("[data-grid-label]")].map((text) => text.textContent)).toEqual([
    "0%",
    "3%",
    "5%",
    "8%",
    "10%",
  ]);
});

test("a ruleset change draws a dashed marker labelled with its year", () => {
  const { container } = renderWithRouter(<LineChart points={points} rulesetChanges={[2025]} label="Trend" />);
  expect(container.querySelectorAll("[data-ruleset-change]")).toHaveLength(1);
  expect(container.querySelector("[data-ruleset-change] + text")).toHaveTextContent("2025");
});

test("one point is drawn without a line", () => {
  const { container } = renderWithRouter(<LineChart points={points.slice(0, 1)} rulesetChanges={[]} label="Trend" />);
  expect(container.querySelectorAll("path")).toHaveLength(0);
  expect(container.querySelectorAll("circle")).toHaveLength(1);
});

test("the y axis ends on a round value above the highest share", () => {
  expect(niceMax(0.07)).toBe(0.1);
  expect(niceMax(0.12)).toBe(0.2);
  expect(niceMax(0.022)).toBe(0.025);
  expect(niceMax(0)).toBe(1);
});
