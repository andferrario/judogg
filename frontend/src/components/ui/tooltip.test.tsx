import { screen } from "@testing-library/react";
import { renderWithMeta } from "../../test/render";
import { InfoTip } from "./InfoTip";
import { TooltipLayer } from "./TooltipLayer";

test("the glossary tip opens on hover and closes when the pointer moves away", async () => {
  const { user } = renderWithMeta(
    <>
      <InfoTip term="Lift" />
      <p>elsewhere</p>
      <TooltipLayer />
    </>,
  );
  await user.hover(screen.getByRole("button", { name: "About Lift" }));
  expect(screen.getByRole("tooltip")).toBeVisible();
  expect(screen.getByRole("tooltip")).toHaveTextContent(/^Lift /);
  await user.hover(screen.getByText("elsewhere"));
  expect(screen.getByRole("tooltip", { hidden: true })).not.toBeVisible();
});

test("the tip opens on keyboard focus, describes the button, and Escape closes it", async () => {
  const { user } = renderWithMeta(
    <>
      <InfoTip term="Lift" />
      <TooltipLayer />
    </>,
  );
  await user.tab();
  const button = screen.getByRole("button", { name: "About Lift" });
  expect(button).toHaveFocus();
  expect(screen.getByRole("tooltip")).toBeVisible();
  expect(button).toHaveAccessibleDescription(/^Lift\s/);
  await user.keyboard("{Escape}");
  expect(screen.getByRole("tooltip", { hidden: true })).not.toBeVisible();
});
