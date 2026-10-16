import type { ReactNode } from "react";
import { InfoTip } from "./InfoTip";
import styles from "./Kpi.module.css";

export function KpiGrid({ label = "Key figures", children }: { label?: string; children: ReactNode }) {
  return (
    <dl className={styles.grid} aria-label={label}>
      {children}
    </dl>
  );
}

type KpiProps = {
  label: string;
  value: ReactNode;
  /** The context of the number, or the question it answers. */
  sub: ReactNode;
  term?: string;
  /** For a value made of several numbers, which would wrap at full size. */
  small?: boolean;
};

export function Kpi({ label, value, sub, term, small = false }: KpiProps) {
  return (
    <div className={styles.kpi}>
      <dt className={styles.label}>
        {label}
        {term && <InfoTip term={term} />}
      </dt>
      <dd className={`${styles.value} num`} data-small={small || undefined}>
        {value}
      </dd>
      <dd className={styles.sub}>{sub}</dd>
    </div>
  );
}
