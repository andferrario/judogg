import type { TierRow } from "../../api/types";
import { ScoreLegend, SideBar, StackedBar } from "../../components/charts/Bars";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { InfoTip } from "../../components/ui/InfoTip";
import { TechniqueLink } from "../../components/ui/links";
import { Loaded } from "../../components/ui/Loaded";
import { sampleState } from "../../components/ui/sample";
import { SortableTh } from "../../components/ui/SortableTh";
import { useFilters } from "../../filters/useFilters";
import { DOMAIN_LABEL, formatCount, formatPercent } from "../../format/format";
import styles from "./TierCard.module.css";
import { sortChange } from "./tierSort";
import { useTierList } from "./useTierList";

// The longest bar takes 80% of its cell: room is left for the share next to it.
const LONGEST_BAR = 0.8;

export function TierCard() {
  const { setPageParams } = useFilters();
  const { query, sort, order, all } = useTierList();
  const onSort = (column: string) => setPageParams(sortChange({ sort, order }, column));
  return (
    <Loaded query={query}>
      {(tier) => {
        const byAthlete = tier.filters.count_by === "athlete";
        const rows = tier.data.rows;
        const max = Math.max(0.0001, ...rows.map((row) => row.share ?? 0));
        const header = { sort, order, onSort };
        return (
          <Card
            title="Top techniques"
            term={byAthlete ? "Share (by athlete)" : "Share (by event)"}
            sample={tier.data.sample}
            right={<ScoreLegend />}
            description={
              byAthlete
                ? "Which techniques the most athletes score with: the share of scoring athletes who scored with each one at least once. Rows below the sample threshold are greyed out."
                : "Which techniques score the most: each technique's share of all the scores in the filter, split by score value. Rows below the sample threshold are greyed out."
            }
          >
            {rows.length === 0 ? (
              <EmptyState>No score with these filters. Widen the filters.</EmptyState>
            ) : (
              <>
                <div className="tw">
                  <table className={styles.table}>
                    <thead>
                      <tr>
                        <th scope="col">Technique</th>
                        <SortableTh column="share" label={byAthlete ? "Share of athletes" : "Share of scores"} {...header} />
                        <SortableTh column="n_scores" label="Scores" numeric {...header} />
                        <SortableTh column="n_athletes" label="Athletes" numeric {...header} />
                        <SortableTh column="pct_ippon" label="% ippon" numeric {...header} />
                        <SortableTh column="pct_waza_ari" label="% waza-ari" numeric {...header} />
                        <SortableTh column="pct_yuko" label="% yuko" numeric {...header} />
                        <th scope="col" className="r">
                          Awasete
                          <InfoTip term="Waza-ari awasete ippon" />
                        </th>
                        <th scope="col" className={styles.center}>
                          Left ← → Right
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((row) => (
                        <TierRowView key={row.technique?.code ?? "unknown"} row={row} max={max} />
                      ))}
                    </tbody>
                  </table>
                </div>
                {(all || tier.data.total_rows > rows.length) && (
                  <div className="more">
                    <button type="button" className="btn" onClick={() => setPageParams({ all: all ? null : "1" })}>
                      {all ? "Show top 15" : `Show all (${tier.data.total_rows})`}
                    </button>
                  </div>
                )}
              </>
            )}
          </Card>
        );
      }}
    </Loaded>
  );
}

function TierRowView({ row, max }: { row: TierRow; max: number }) {
  const technique = row.technique;
  const family = technique
    ? [technique.group_label, technique.domain && DOMAIN_LABEL[technique.domain]].filter(Boolean).join(" · ")
    : "no technique tag";
  return (
    <tr data-sample={sampleState(row.sample)}>
      <th scope="row">
        <TechniqueLink technique={technique} />
        <span className="fam">{family}</span>
      </th>
      <td className={styles.shareCell}>
        <div className={styles.share}>
          <StackedBar
            counts={row.counts}
            fraction={((row.share ?? 0) / max) * LONGEST_BAR}
            tip={`${row.n_scores} scores · ${row.n_athletes} athletes\nIppon ${row.counts.ippon} · Waza-ari ${row.counts.waza_ari} · Yuko ${row.counts.yuko}`}
          />
          <span className="num">{formatPercent(row.share, 1)}</span>
        </div>
      </td>
      <td className="r num">{formatCount(row.n_scores)}</td>
      <td className="r num">{formatCount(row.n_athletes)}</td>
      <td className="r num">{formatPercent(row.pct.ippon)}</td>
      <td className="r num">{formatPercent(row.pct.waza_ari)}</td>
      <td className="r num">{formatPercent(row.pct.yuko)}</td>
      <td className="r num">{row.n_awasete || "–"}</td>
      <td>
        <SideBar side={row.side} />
      </td>
    </tr>
  );
}
