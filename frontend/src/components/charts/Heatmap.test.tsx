import { screen } from "@testing-library/react";
import { currentPath, lastNavigation, renderWithRouter } from "../../test/render";
import { DivergingLegend, divergingFill, Heatmap, sequentialFill, type HeatRow } from "./Heatmap";

const cell = {
  key: "seoi_nage",
  text: "14%",
  fill: sequentialFill(0.8),
  tip: "-60 M · Seoi-nage\n13.6% (8 of 59 scores)",
  label: "-60 M · Seoi-nage: 13.6% (8 of 59 scores)",
  to: { pathname: "/techniques/seoi_nage", search: "?weight=m-60&gender=m" },
};
const rows: HeatRow[] = [
  { key: "m-60", label: "-60 M", dimmed: false, cells: [cell, null] },
  { key: "f+78", label: "+78 W", dimmed: true, cells: [null, { ...cell, key: "x", label: "+78 W · x", text: "0%" }] },
];
const columns = [
  { key: "seoi_nage", label: "Seoi-nage" },
  { key: "x", label: "X" },
];

test("each cell is a link named by its row, column and value, coloured by its fill", () => {
  renderWithRouter(<Heatmap columns={columns} rows={rows} />);
  const link = screen.getByRole("link", { name: "-60 M · Seoi-nage: 13.6% (8 of 59 scores)" });
  expect(link).toHaveAttribute("href", "/techniques/seoi_nage?weight=m-60&gender=m");
  expect(link).toHaveTextContent("14%");
  expect(link.style.color).toBe("var(--on-hi)");
});

test("empty cells are not links; dimmed rows are marked", () => {
  const { container } = renderWithRouter(<Heatmap columns={columns} rows={rows} />);
  expect(screen.getAllByRole("link")).toHaveLength(2);
  expect(container.querySelectorAll("[data-empty]")).toHaveLength(2);
  expect(screen.getByRole("link", { name: "+78 W · x" })).toHaveAttribute("data-dimmed");
});

test("cells can replace the history entry instead of pushing one", async () => {
  const { user } = renderWithRouter(<Heatmap columns={columns} rows={rows} replace />, "/techniques");
  await user.click(screen.getByRole("link", { name: /^-60 M/ }));
  expect(currentPath()).toBe("/techniques/seoi_nage?weight=m-60&gender=m");
  expect(lastNavigation()).toBe("REPLACE");
});

test("the sequential fill mixes the two scale tokens", () => {
  expect(sequentialFill(0.5)).toEqual({
    background: "color-mix(in oklab, var(--seq-hi) 50%, var(--seq-lo))",
    lightText: false,
  });
  expect(sequentialFill(1.7).background).toBe("color-mix(in oklab, var(--seq-hi) 100%, var(--seq-lo))");
});

test("the diverging fill is symmetric around a lift of 1, capped at twice or half", () => {
  expect(divergingFill(2)).toEqual({ background: "color-mix(in oklab, var(--div-pos) 100%, var(--div-mid))", lightText: true });
  expect(divergingFill(0.5)).toEqual({ background: "color-mix(in oklab, var(--div-neg) 100%, var(--div-mid))", lightText: true });
  expect(divergingFill(8)).toEqual(divergingFill(2));
  expect(divergingFill(1)).toEqual({ background: "color-mix(in oklab, var(--div-pos) 0%, var(--div-mid))", lightText: false });
  expect(divergingFill(null)).toEqual(divergingFill(1));
  expect(divergingFill(0)).toEqual(divergingFill(0.5));
});

test("the diverging legend names its three colours", () => {
  renderWithRouter(<DivergingLegend />);
  for (const text of ["below 1", "1", "above 1"]) expect(screen.getByText(text)).toBeInTheDocument();
});
