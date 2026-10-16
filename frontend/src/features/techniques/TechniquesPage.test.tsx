import { screen, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { invalidWeightError, overview } from "../../test/fixtures";
import { renderApp } from "../../test/render";
import { server } from "../../test/server";

const DEFAULT_SUMMARY = "Men and women · all weights · rules 2025– · 2025–2027";

test("the header summarises the filters the API applied", async () => {
  renderApp("/techniques");
  expect(await screen.findByText(DEFAULT_SUMMARY)).toBeInTheDocument();
});

test("the warnings of the response are shown under the header", async () => {
  renderApp("/techniques");
  expect(await screen.findByText("3 contests in the filter have inconsistent IJF data.")).toBeInTheDocument();
});

test("a hand-edited invalid URL shows Invalid filters, the rail stays usable, the reset recovers", async () => {
  server.use(
    http.get("/api/overview", ({ request }) =>
      new URL(request.url).searchParams.get("gender") === "f"
        ? HttpResponse.json(invalidWeightError, { status: 400 })
        : HttpResponse.json(overview),
    ),
  );
  const { user } = renderApp("/techniques?gender=f&weight=m-73");
  const alert = await screen.findByRole("alert");
  expect(alert).toHaveTextContent("Invalid filters. weight category m-73 does not match gender f");
  expect(screen.getByRole("group", { name: "Gender" })).toBeInTheDocument();
  await user.click(within(alert).getByRole("link", { name: "Reset filters" }));
  expect(await screen.findByText(DEFAULT_SUMMARY)).toBeInTheDocument();
});

test("a server failure offers a retry", async () => {
  server.use(http.get("/api/overview", () => new HttpResponse(null, { status: 500 }), { once: true }));
  const { user } = renderApp("/techniques");
  await user.click(await screen.findByRole("button", { name: "Retry" }));
  expect(await screen.findByText(DEFAULT_SUMMARY)).toBeInTheDocument();
});

test("the KPIs explain the data behind the page", async () => {
  renderApp("/techniques");
  const kpis = await screen.findByLabelText("Key figures");
  for (const text of [
    "756",
    "546 fought · 24% to golden score",
    "278",
    "athletes with at least one score · 58 different techniques",
    "8%",
    "17%",
    "left out of the left/right bars",
  ]) {
    expect(kpis).toHaveTextContent(text);
  }
  expect(within(kpis).getByRole("button", { name: "About Unknown technique" })).toBeInTheDocument();
});
