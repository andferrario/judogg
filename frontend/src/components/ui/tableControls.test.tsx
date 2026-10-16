import { screen } from "@testing-library/react";
import { renderWithRouter } from "../../test/render";
import { Pagination } from "./Pagination";
import { SortableTh } from "./SortableTh";

function header(sort: string, order: "asc" | "desc", onSort = vi.fn()) {
  return renderWithRouter(
    <table>
      <thead>
        <tr>
          <SortableTh label="Scores" column="n_scores" sort={sort} order={order} onSort={onSort} numeric />
        </tr>
      </thead>
    </table>,
  );
}

test("the active column carries aria-sort and an arrow", () => {
  header("n_scores", "asc");
  const th = screen.getByRole("columnheader", { name: "Scores" });
  expect(th).toHaveAttribute("aria-sort", "ascending");
  expect(th).toHaveTextContent("Scores ↑");
});

test("another column has no aria-sort and asks to sort on click", async () => {
  const onSort = vi.fn();
  const { user } = header("share", "desc", onSort);
  expect(screen.getByRole("columnheader", { name: "Scores" })).not.toHaveAttribute("aria-sort");
  await user.click(screen.getByRole("button", { name: "Scores" }));
  expect(onSort).toHaveBeenCalledWith("n_scores");
});

test("pagination disables what cannot be reached and asks for the other pages", async () => {
  const onPage = vi.fn();
  const { user, rerender } = renderWithRouter(<Pagination page={1} pages={3} onPage={onPage} />);
  const nav = screen.getByRole("navigation", { name: "Pages" });
  expect(nav).toHaveTextContent("page 1 of 3");
  expect(screen.getByRole("button", { name: "← Previous" })).toBeDisabled();
  await user.click(screen.getByRole("button", { name: "Next →" }));
  expect(onPage).toHaveBeenCalledWith(2);
  rerender(<Pagination page={3} pages={3} onPage={onPage} />);
  expect(screen.getByRole("button", { name: "Next →" })).toBeDisabled();
});
