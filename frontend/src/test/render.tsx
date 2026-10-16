import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { MemoryRouter, useLocation, useNavigationType } from "react-router";
import { createQueryClient } from "../api/queryClient";
import { App } from "../app/App";
import { MetaProvider } from "../app/meta";
import { meta } from "./fixtures";

export function renderApp(url: string) {
  return renderAt(url, <App />);
}

export function renderWithRouter(ui: ReactNode, url = "/") {
  return renderAt(url, ui);
}

export function renderWithMeta(ui: ReactNode, url = "/") {
  return renderAt(url, <MetaProvider meta={meta}>{ui}</MetaProvider>);
}

export function currentPath(): string {
  return screen.getByTestId("location").textContent ?? "";
}

export function currentParams(): Record<string, string> {
  return Object.fromEntries(new URLSearchParams(currentPath().split("?")[1] ?? ""));
}

export function lastNavigation(): string | undefined {
  return screen.getByTestId("location").dataset.navigation;
}

function renderAt(url: string, ui: ReactNode) {
  const user = userEvent.setup();
  const client = testQueryClient();
  const wrap = (node: ReactNode) => (
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[url]} useTransitions={false}>
        {node}
        <LocationProbe />
      </MemoryRouter>
    </QueryClientProvider>
  );
  const view = render(wrap(ui));
  return { user, container: view.container, rerender: (node: ReactNode) => view.rerender(wrap(node)) };
}

// Retries would turn every failing request of a test into seconds of waiting.
function testQueryClient() {
  const client = createQueryClient();
  client.setDefaultOptions({ queries: { ...client.getDefaultOptions().queries, retry: false } });
  return client;
}

function LocationProbe() {
  const { pathname, search } = useLocation();
  const navigation = useNavigationType();
  return (
    <span data-testid="location" data-navigation={navigation}>
      {pathname + search}
    </span>
  );
}
