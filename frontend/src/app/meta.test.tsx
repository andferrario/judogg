import { screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { renderApp } from "../test/render";
import { server } from "../test/server";

test("the app waits for the metadata before showing the pages", async () => {
  renderApp("/techniques");
  expect(screen.getByRole("status")).toHaveTextContent("Loading…");
  expect(await screen.findByRole("heading", { level: 1, name: "Techniques" })).toBeInTheDocument();
});

test("a failed metadata request offers a retry instead of a blank page", async () => {
  server.use(http.get("/api/meta", () => new HttpResponse(null, { status: 500 }), { once: true }));
  const { user } = renderApp("/techniques");
  await user.click(await screen.findByRole("button", { name: "Retry" }));
  expect(await screen.findByRole("heading", { level: 1, name: "Techniques" })).toBeInTheDocument();
});
