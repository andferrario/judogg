import type { UseQueryResult } from "@tanstack/react-query";
import type { ReactNode } from "react";
import type { ApiFilters, WarningItem } from "../api/types";
import { ErrorBox } from "../components/ui/ErrorBox";
import { PageHeader } from "../components/ui/PageHeader";
import { Skeleton } from "../components/ui/Skeleton";
import { Warnings } from "../components/ui/Warnings";
import { filterSummary } from "../filters/filters";
import { useMetaData } from "./meta";
import styles from "./PageFrame.module.css";

type Envelope = { filters: ApiFilters; warnings: WarningItem[] };
type PageFrameProps<T extends Envelope> = {
  title: string;
  query: UseQueryResult<T>;
  big?: boolean;
  back?: ReactNode;
  aside?: ReactNode;
  subtitle?: (data: T) => string | undefined;
  children?: (data: T) => ReactNode;
};

export function PageFrame<T extends Envelope>({ title, query, big, back, aside, subtitle, children }: PageFrameProps<T>) {
  const meta = useMetaData();
  const header = (summary?: string) => (
    <PageHeader title={title} summary={summary} big={big} back={back}>
      {aside}
    </PageHeader>
  );
  if (query.isError) {
    return (
      <>
        {header()}
        <ErrorBox error={query.error} onRetry={() => void query.refetch()} retrying={query.isFetching} />
      </>
    );
  }
  if (query.data === undefined) {
    return (
      <>
        {header()}
        <Skeleton />
      </>
    );
  }
  const summary = [subtitle?.(query.data), filterSummary(query.data.filters, meta)].filter(Boolean).join(" · ");
  return (
    <>
      {header(summary)}
      <Warnings warnings={query.data.warnings} />
      <PageContent refreshing={query.isPlaceholderData}>{children?.(query.data)}</PageContent>
    </>
  );
}

export function PageContent({ refreshing, children }: { refreshing: boolean; children: ReactNode }) {
  return (
    <div className={styles.content} data-refreshing={refreshing || undefined}>
      {children}
    </div>
  );
}
