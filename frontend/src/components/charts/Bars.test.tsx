import { screen } from "@testing-library/react";
import { renderWithRouter } from "../../test/render";
import { HBar, MiniSide, ScoreLegend, SideBar, SideLegend, SplitBar, StackedBar, widthOf } from "./Bars";

test("a stacked bar has one segment per score value present, sized by its count", () => {
  const { container } = renderWithRouter(
    <StackedBar counts={{ ippon: 14, waza_ari: 27, yuko: 0 }} fraction={0.5} tip="75 scores" />,
  );
  const bar = container.querySelector("[data-tip='75 scores']") as HTMLElement;
  expect(bar.style.width).toBe("50%");
  expect([...bar.querySelectorAll("i")].map((segment) => segment.style.flexGrow)).toEqual(["14", "27"]);
});

test("the side bar shows the left and right shares of the known sides", () => {
  renderWithRouter(<SideBar side={{ left: 44, right: 28, unknown: 3 }} />);
  expect(screen.getByText("61%")).toBeInTheDocument();
  expect(screen.getByText("39%")).toBeInTheDocument();
  expect(screen.getByText("61%").parentElement).toHaveAttribute(
    "data-tip",
    "Left 44 · Right 28 · Unknown 3 (4%)",
  );
});

test("without a known side the side bar shows dashes", () => {
  renderWithRouter(<SideBar side={{ left: 0, right: 0, unknown: 5 }} />);
  expect(screen.getAllByText("–")).toHaveLength(2);
});

test("the mini side bar says its counts", () => {
  renderWithRouter(<MiniSide side={{ left: 2, right: 3, unknown: 0 }} />);
  expect(screen.getByRole("img", { name: "Left 2 · Right 3 · Unknown 0" }).children).toHaveLength(2);
});

test("a dimmed bar is marked, widths stay between 0 and 100%", () => {
  const { container } = renderWithRouter(<HBar fraction={1.4} dimmed />);
  const bar = container.querySelector("[data-dimmed]") as HTMLElement;
  expect(bar.style.width).toBe("100%");
  expect(widthOf(-0.2)).toBe("0%");
});

test("the legends name the colours", () => {
  renderWithRouter(
    <>
      <ScoreLegend />
      <SideLegend />
    </>,
  );
  for (const label of ["Ippon", "Waza-ari", "Yuko", "Left", "Right", "Unknown"]) {
    expect(screen.getByText(label)).toBeInTheDocument();
  }
});

test("the values of a bar's tooltip are also in the page as text", () => {
  renderWithRouter(
    <>
      <StackedBar counts={{ ippon: 1, waza_ari: 0, yuko: 0 }} fraction={0.5} tip="1 score · Ippon 1" />
      <HBar fraction={0.3} tip="-66 M: 5 of 125 scores (4.0%)" />
      <SideBar side={{ left: 44, right: 28, unknown: 3 }} />
    </>,
  );
  expect(screen.getByText("1 score · Ippon 1")).toHaveClass("sr");
  expect(screen.getByText("-66 M: 5 of 125 scores (4.0%)")).toHaveClass("sr");
  expect(screen.getByText("Left 44 · Right 28 · Unknown 3 (4%)")).toHaveClass("sr");
});

test("a split bar shows each part's share in the legend, its count as hidden text", () => {
  const { container } = renderWithRouter(
    <SplitBar
      parts={[
        { key: "passivity", label: "Passivity", n: 724, share: 0.7487 },
        { key: "other", label: "Other", n: 1, share: 0.001 },
      ]}
    />,
  );
  expect(screen.getByText("Passivity 75%")).toBeInTheDocument();
  expect(screen.getByText("Other 0%")).toBeInTheDocument();
  const [passivity, other] = container.querySelectorAll<HTMLElement>("[data-part]");
  expect(passivity.textContent).toBe("Passivity: 724 (74.9%)");
  expect(other.textContent).toBe("Other: 1 (0.1%)");
  expect(other).toHaveAttribute("data-tip", "Other: 1 (0.1%)");
});

test("a penalty bar has the penalty tone", () => {
  const { container } = renderWithRouter(<HBar fraction={0.5} tone="penalty" />);
  expect(container.querySelector("[data-tone='penalty']")).not.toBeNull();
});

test("the counts of a split bar are also in the page as text", () => {
  renderWithRouter(<SplitBar parts={[{ key: "grip", label: "Grip", n: 201, share: 0.2079 }]} />);
  expect(screen.getByText("Grip: 201 (20.8%)")).toHaveClass("sr");
});
