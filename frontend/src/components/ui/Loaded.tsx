import type { UseQueryResult } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { ErrorBox } from "./ErrorBox";
import { Skeleton } from "./Skeleton";

type LoadedProps<T> = { query: UseQueryResult<T>; children: (data: T) => ReactNode };

// One card, one query: a failing endpoint breaks its card, not the page.
export function Loaded<T>({ query, children }: LoadedProps<T>) {
  if (query.isError) {
    return <ErrorBox error={query.error} onRetry={() => void query.refetch()} retrying={query.isFetching} />;
  }
  if (query.data === undefined) return <Skeleton blocks={1} />;
  return <>{children(query.data)}</>;
}
