import { createContext, use, type ReactNode } from "react";
import { useMeta } from "../api/hooks";
import type { Meta } from "../api/types";
import { ErrorBox } from "../components/ui/ErrorBox";
import { Skeleton } from "../components/ui/Skeleton";
import styles from "./MetaGate.module.css";

const MetaContext = createContext<Meta | null>(null);

export function MetaProvider({ meta, children }: { meta: Meta; children: ReactNode }) {
  return <MetaContext value={meta}>{children}</MetaContext>;
}

// Filters, search and labels all need the metadata: nothing renders before it.
export function MetaGate({ children }: { children: ReactNode }) {
  const meta = useMeta();
  if (meta.isError) {
    return (
      <div className={styles.alone}>
        <ErrorBox error={meta.error} onRetry={() => void meta.refetch()} retrying={meta.isFetching} />
      </div>
    );
  }
  if (meta.isPending) {
    return (
      <div className={styles.alone}>
        <Skeleton />
      </div>
    );
  }
  return <MetaProvider meta={meta.data}>{children}</MetaProvider>;
}

export function useMetaData(): Meta {
  const meta = use(MetaContext);
  if (meta === null) throw new Error("useMetaData needs a MetaGate or a MetaProvider above it");
  return meta;
}
