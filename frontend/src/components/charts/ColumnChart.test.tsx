import { screen, within } from "@testing-library/react";
import { overview, penalties } from "../../test/fixtures";
import { renderWithRouter } from "../../test/render";
import { ColumnChart } from "./ColumnChart";

const bins = overview.data.timing;

test("the chart is an image named by its label, its values readable as text", () => {
  renderWithRouter(<ColumnChart bins={bins} label="Scores per 30-second block" />);
  expect(screen.getByRole("img", { name: "Scores per 30-second block" })).toBeInTheDocument();
  const values = screen.getByRole("list", { name: "Scores per 30-second block: values" });
  expect(within(values).getAllByRole("listitem")).toHaveLength(9);
  expect(values).toHaveTextContent("0:00–0:30: 67 scores (Ippon 19, Waza-ari 20, Yuko 28)");
  expect(values).toHaveTextContent("Golden score: 102 scores (Ippon 24, Waza-ari 29, Yuko 49)");
});

test("the x axis starts every block and calls the last one GS, after a separator", () => {
  const { container } = renderWithRouter(<ColumnChart bins={bins} label="Timing" />);
  expect(container.querySelectorAll("[data-axis] span")).toHaveLength(9);
  expect(container.querySelector("[data-axis]")).toHaveTextContent("0:000:301:001:302:002:303:003:30GS");
  expect(container.querySelectorAll("[data-gs]")).toHaveLength(2);
});

test("column heights are proportional to the tallest column", () => {
  const { container } = renderWithRouter(<ColumnChart bins={bins} label="Timing" />);
  const heights = [...container.querySelectorAll<HTMLElement>("[data-stack]")].map((stack) => stack.style.height);
  const tallest = Math.max(...bins.map((bin) => bin.n));
  const index = bins.findIndex((bin) => bin.n === tallest);
  expect(heights[index]).toBe("85%");
});

test("penalty bins are one series, described as penalties", () => {
  renderWithRouter(<ColumnChart bins={penalties.data.timing} label="Penalties per 30-second block" />);
  const values = screen.getByRole("list", { name: "Penalties per 30-second block: values" });
  expect(values).toHaveTextContent("0:00–0:30: 38 penalties");
  expect(values).toHaveTextContent("Golden score: 103 penalties");
});
