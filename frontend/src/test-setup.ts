import "@testing-library/jest-dom/vitest";
import { configure } from "@testing-library/react";
import { server } from "./test/server";

// A page renders many cards, each with its own request: under a parallel test run one second is not enough.
configure({ asyncUtilTimeout: 5000 });

// jsdom does not implement scrolling.
window.scrollTo = () => {};

beforeAll(() => server.listen({ onUnhandledFrame: "error" }));
afterEach(() => {
  server.resetHandlers();
  localStorage.clear();
});
afterAll(() => server.close());
