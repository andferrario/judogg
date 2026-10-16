import type { UseQueryResult } from "@tanstack/react-query";
import { screen } from "@testing-library/react";
import { renderWithRouter } from "../../test/render";
import { AthleteLink, TechniqueLink } from "./links";
import { Loaded } from "./Loaded";
import { Notice } from "./Notice";
import { sampleState } from "./sample";

const uchiMata = { code: "uchi_mata", name: "Uchi-mata", group_label: "Ashi-waza", domain: "standing" as const };
const athlete = { id: 900323, given_name: "Tagi", family_name: "SADIDI", country_code: "AZE" };

test("a technique link opens the technique page with the filters, not the page parameters", () => {
  renderWithRouter(<TechniqueLink technique={uchiMata} />, "/techniques?gender=m&trend=x");
  expect(screen.getByRole("link", { name: "Uchi-mata" })).toHaveAttribute("href", "/techniques/uchi_mata?gender=m");
});

test("the Unknown row is plain text, never a link", () => {
  renderWithRouter(<TechniqueLink technique={null} />);
  expect(screen.getByText("Unknown technique")).toBeInTheDocument();
  expect(screen.queryByRole("link")).not.toBeInTheDocument();
});

test("an athlete link opens the judoka page with the filters, followed by the country code", () => {
  renderWithRouter(<AthleteLink athlete={athlete} />, "/techniques?gender=m");
  expect(screen.getByRole("link", { name: "Tagi SADIDI" })).toHaveAttribute("href", "/athletes/900323?gender=m");
  expect(screen.getByText("AZE")).toBeInTheDocument();
});

const query = (state: Partial<UseQueryResult<string>>) => state as UseQueryResult<string>;

test("Loaded shows a skeleton, then the content", () => {
  const { rerender } = renderWithRouter(<Loaded query={query({ isError: false, data: undefined })}>{(text) => <p>{text}</p>}</Loaded>);
  expect(screen.getByRole("status")).toHaveTextContent("Loading…");
  rerender(<Loaded query={query({ isError: false, data: "ready" })}>{(text) => <p>{text}</p>}</Loaded>);
  expect(screen.getByText("ready")).toBeInTheDocument();
});

test("Loaded shows the error box with a retry", () => {
  const refetch = vi.fn();
  renderWithRouter(
    <Loaded query={query({ isError: true, error: new Error("The API answered 500"), refetch, isFetching: false })}>
      {(text) => <p>{text}</p>}
    </Loaded>,
  );
  expect(screen.getByRole("alert")).toHaveTextContent("Something went wrong.");
});

test("a notice is a note", () => {
  renderWithRouter(<Notice>Hold-downs score by time.</Notice>);
  expect(screen.getByRole("note")).toHaveTextContent("Hold-downs score by time.");
});

test("sampleState marks only the samples below the thresholds", () => {
  expect(sampleState({ status: "ok", n: 30, unit: "scores" })).toBeUndefined();
  expect(sampleState({ status: "small", n: 8, unit: "scores" })).toBe("small");
  expect(sampleState(undefined)).toBeUndefined();
});
