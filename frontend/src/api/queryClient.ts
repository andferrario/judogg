import { QueryClient } from "@tanstack/react-query";
import { ApiError } from "./client";

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // The data changes only when the database is reloaded; a page reload refetches.
        staleTime: Infinity,
        refetchOnWindowFocus: false,
        // An answer of the API (a bad filter, an unknown technique) does not change on retry.
        retry: (failures, error) => !(error instanceof ApiError) && failures < 2,
      },
    },
  });
}
