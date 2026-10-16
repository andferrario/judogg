import { screen } from "@testing-library/react";
import { useOverview } from "../api/hooks";
import { useFilters } from "../filters/useFilters";
import { renderWithMeta } from "../test/render";
import { PageFrame } from "./PageFrame";

function Page() {
  const { filters } = useFilters();
  return (
    <PageFrame
      title="Uchi-mata"
      big
      query={useOverview(filters)}
      back={<a href="/techniques">← Techniques</a>}
      aside={<span>aside</span>}
      subtitle={() => "Ashi-waza · Standing"}
    />
  );
}

test("the frame shows the back link, a big title, the aside and the subtitle before the filter summary", async () => {
  renderWithMeta(<Page />);
  expect(screen.getByRole("link", { name: "← Techniques" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { level: 1, name: "Uchi-mata" })).toHaveAttribute("data-big");
  expect(screen.getByText("aside")).toBeInTheDocument();
  expect(
    await screen.findByText("Ashi-waza · Standing · Men and women · all weights · rules 2025– · 2025–2027"),
  ).toBeInTheDocument();
});
