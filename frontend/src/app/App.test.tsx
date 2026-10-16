import { screen, within } from "@testing-library/react";
import { savedFilters } from "../filters/persistence";
import { currentPath, renderApp } from "../test/render";

test("the root redirects to Techniques, keeping the query", async () => {
  renderApp("/?gender=m");
  expect(await screen.findByRole("heading", { level: 1, name: "Techniques" })).toBeInTheDocument();
  expect(currentPath()).toBe("/techniques?gender=m");
});

test.each([
  ["/techniques", "Techniques"],
  ["/techniques/uchi_mata", "Uchi-mata"],
  ["/repertoire", "Repertoire"],
  ["/penalties", "Penalties"],
  ["/coverage", "Coverage"],
  ["/athletes/900323", "Tagi SADIDI"],
])("%s shows the %s page", async (url, title) => {
  renderApp(url);
  expect(await screen.findByRole("heading", { level: 1, name: title })).toBeInTheDocument();
});

test("the header marks the current section, technique pages included", async () => {
  renderApp("/techniques/uchi_mata");
  expect(await screen.findByRole("link", { name: "Techniques" })).toHaveAttribute("aria-current", "page");
  expect(screen.getByRole("link", { name: "Repertoire" })).not.toHaveAttribute("aria-current");
});

test("an unknown route shows Page not found, with a link that keeps the filters", async () => {
  renderApp("/nope?gender=m&trend=x");
  expect(await screen.findByRole("alert")).toHaveTextContent("Page not found.");
  expect(screen.getByRole("link", { name: "Go to Techniques" })).toHaveAttribute("href", "/techniques?gender=m");
});

test("the header links keep the filters and drop the page parameters", async () => {
  renderApp("/techniques?gender=m&weight=m-73,m-81&trend=uchi_mata");
  expect(await screen.findByRole("link", { name: "Repertoire" })).toHaveAttribute(
    "href",
    "/repertoire?gender=m&weight=m-73,m-81",
  );
  expect(screen.getByRole("link", { name: "Judogg" })).toHaveAttribute("href", "/techniques?gender=m&weight=m-73,m-81");
});

test("the filters of the URL are saved for the next visit", async () => {
  renderApp("/penalties?gender=f&reason=hitting");
  await screen.findByRole("heading", { level: 1, name: "Penalties" });
  expect(savedFilters()).toEqual({ gender: "f" });
});

test("a new page starts at the top; a filter change keeps the scroll position", async () => {
  const scrollTo = vi.spyOn(window, "scrollTo").mockImplementation(() => {});
  const { user } = renderApp("/techniques");
  await user.click(within(await screen.findByRole("group", { name: "Gender" })).getByRole("button", { name: "Men" }));
  expect(scrollTo).not.toHaveBeenCalled();
  await user.click(screen.getByRole("link", { name: "Penalties" }));
  expect(scrollTo).toHaveBeenCalledWith(0, 0);
});
