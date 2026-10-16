import { useId } from "react";
import { useOverview } from "../api/hooks";
import { formatCount } from "../format/format";
import styles from "./DataStrip.module.css";
import { useFilters } from "./useFilters";

const TOTALS = [
  { key: "competitions", one: "competition", many: "competitions" },
  { key: "contests", one: "contest", many: "contests" },
  { key: "athletes", one: "judoka", many: "judoka" },
  { key: "scores", one: "score", many: "scores" },
  { key: "penalties", one: "penalty", many: "penalties" },
] as const;

// Every analytical endpoint answers the same totals for the same filters: the overview stands for all pages.
export function DataStrip() {
  const titleId = useId();
  const { filters } = useFilters();
  const totals = useOverview(filters).data?.totals;
  return (
    <div className={styles.strip} role="status" aria-labelledby={titleId}>
      <p id={titleId} className={styles.title}>
        In this filter
      </p>
      {totals && (
        <>
          <p className={styles.values}>
            {TOTALS.map(({ key, one, many }) => (
              <span key={key}>
                <b className="num">{formatCount(totals[key])}</b> {totals[key] === 1 ? one : many}
              </span>
            ))}
          </p>
          <p className={styles.note}>Side and technique type filter the scores only.</p>
        </>
      )}
    </div>
  );
}
