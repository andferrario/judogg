import "./styles/tokens.css";
import "./styles/base.css";
import { QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import { createQueryClient } from "./api/queryClient";
import { App } from "./app/App";
import { searchWithSavedFilters } from "./filters/persistence";

// Restored before the router starts, so that the first render already has the filters.
const restored = searchWithSavedFilters(window.location.search);
if (restored !== null) {
  window.history.replaceState(null, "", `${window.location.pathname}${restored}${window.location.hash}`);
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={createQueryClient()}>
      {/* The URL is the filter state: every component must see a change at once. A transition would let
          fast typing or clicking render with the previous URL and navigate from it, dropping the change. */}
      <BrowserRouter useTransitions={false}>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
