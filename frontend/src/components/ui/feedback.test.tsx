import { screen } from "@testing-library/react";
import { ApiError } from "../../api/client";
import { invalidWeightError } from "../../test/fixtures";
import { currentPath, lastNavigation, renderWithRouter } from "../../test/render";
import { EmptyState } from "./EmptyState";
import { ErrorBox } from "./ErrorBox";
import { Skeleton } from "./Skeleton";
import { Warnings } from "./Warnings";

describe("ErrorBox", () => {
  test("invalid filters offer a reset that keeps the page parameters", async () => {
    const { user } = renderWithRouter(
      <ErrorBox error={new ApiError(400, invalidWeightError.error)} />,
      "/techniques?gender=f&weight=m-73&trend=uchi_mata&v_page=2",
    );
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Invalid filters. weight category m-73 does not match gender f",
    );
    await user.click(screen.getByRole("link", { name: "Reset filters" }));
    expect(currentPath()).toBe("/techniques?trend=uchi_mata");
    expect(lastNavigation()).toBe("REPLACE");
  });

  test("not found links to Techniques, keeping the filters", () => {
    const notFound = new ApiError(404, { code: "not_found", message: "unknown technique: foo", field: "technique" });
    renderWithRouter(<ErrorBox error={notFound} />, "/techniques/foo?gender=m&v_score=ippon");
    expect(screen.getByRole("alert")).toHaveTextContent("Not found. unknown technique: foo");
    expect(screen.getByRole("link", { name: "Go to Techniques" })).toHaveAttribute("href", "/techniques?gender=m");
  });

  test("any other failure offers a retry", async () => {
    const onRetry = vi.fn();
    const { user } = renderWithRouter(<ErrorBox error={new Error("The API answered 500")} onRetry={onRetry} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Something went wrong.");
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledOnce();
  });
  test("a retry in progress is shown and cannot be clicked again", () => {
    renderWithRouter(<ErrorBox error={new Error("The API answered 500")} onRetry={() => {}} retrying />);
    expect(screen.getByRole("button", { name: "Retrying…" })).toBeDisabled();
  });
});

test("warnings are heads-up messages in a status region", () => {
  renderWithRouter(<Warnings warnings={[{ code: "quality_issues", message: "3 contests have inconsistent data." }]} />);
  expect(screen.getByRole("status")).toHaveTextContent("Heads-up. 3 contests have inconsistent data.");
});

test("an empty state says what to change", () => {
  renderWithRouter(<EmptyState>Widen the filters.</EmptyState>);
  expect(screen.getByText("Widen the filters.")).toBeInTheDocument();
});

test("a skeleton announces the loading", () => {
  renderWithRouter(<Skeleton />);
  expect(screen.getByRole("status")).toHaveTextContent("Loading…");
});
