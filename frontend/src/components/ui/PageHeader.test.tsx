import { screen } from "@testing-library/react";
import { renderWithRouter } from "../../test/render";
import { PageHeader } from "./PageHeader";

test("the summary can hold links, and a second line follows it", () => {
  renderWithRouter(
    <PageHeader
      title="Tagi SADIDI"
      summary={
        <>
          AZE · <a href="https://judobase.ijf.org">JudoBase profile ↗</a>
        </>
      }
      note="Whole career in the database, not filtered."
    />,
  );
  expect(screen.getByRole("link", { name: "JudoBase profile ↗" }).closest("p")).toHaveTextContent("AZE · JudoBase profile ↗");
  expect(screen.getByText("Whole career in the database, not filtered.")).toBeInTheDocument();
});
