import { screen, within } from "@testing-library/react";
import { renderWithMeta } from "../../test/render";
import { Card } from "./Card";
import { InfoTip } from "./InfoTip";
import { Kpi, KpiGrid } from "./Kpi";

test("a card shows its title, description, glossary tip and content", () => {
  renderWithMeta(
    <Card title="Top techniques" description="Which techniques score most." term="Lift">
      <p>body</p>
    </Card>,
  );
  const card = screen.getByRole("region", { name: "Top techniques" });
  expect(card).toHaveTextContent("Which techniques score most.");
  expect(within(card).getByText("body")).toBeInTheDocument();
  expect(within(card).getByRole("button", { name: "About Lift" })).toBeInTheDocument();
});

test("a small sample shows a badge and leaves the card readable", () => {
  renderWithMeta(
    <Card title="Trend" description="d" sample={{ status: "small", n: 8, unit: "scores" }}>
      x
    </Card>,
  );
  const card = screen.getByRole("region", { name: "Trend" });
  expect(card).toHaveAttribute("data-sample", "small");
  expect(within(card).getByText("small sample · n=8")).toHaveAttribute(
    "data-tip",
    "Small sample: 8 scores. Read with care.",
  );
});

test("an insufficient sample greys the card out, never hides it", () => {
  renderWithMeta(
    <Card title="Repertoire" description="d" sample={{ status: "insufficient", n: 3, unit: "athletes" }}>
      x
    </Card>,
  );
  const card = screen.getByRole("region", { name: "Repertoire" });
  expect(card).toHaveAttribute("data-sample", "insufficient");
  expect(within(card).getByText("x")).toBeInTheDocument();
  expect(within(card).getByText("insufficient · n=3")).toHaveAttribute(
    "data-tip",
    "Insufficient sample: 3 athletes. Not meaningful.",
  );
});

test("an ok sample shows no badge", () => {
  renderWithMeta(
    <Card title="Ok" description="d" sample={{ status: "ok", n: 80, unit: "scores" }}>
      x
    </Card>,
  );
  expect(screen.queryByText(/n=80/)).not.toBeInTheDocument();
});

test("a KPI is a term with its value and its explanation", () => {
  renderWithMeta(
    <KpiGrid>
      <Kpi label="Scores" value="756" sub="in 556 contests" term="Score" />
    </KpiGrid>,
  );
  expect(screen.getByRole("term")).toHaveTextContent("Scores");
  expect(screen.getAllByRole("definition").map((item) => item.textContent)).toEqual(["756", "in 556 contests"]);
  expect(screen.getByRole("button", { name: "About Score" })).toBeInTheDocument();
});

test("a term missing from the glossary shows no tip", () => {
  renderWithMeta(<InfoTip term="No such term" />);
  expect(screen.queryByRole("button")).not.toBeInTheDocument();
});

test("a KPI with a long value can ask for a smaller font", () => {
  renderWithMeta(
    <KpiGrid>
      <Kpi label="Ippon · waza · yuko" value="21% · 35% · 44%" sub="overall ippon 28%" small />
    </KpiGrid>,
  );
  expect(screen.getByText("21% · 35% · 44%")).toHaveAttribute("data-small");
});
