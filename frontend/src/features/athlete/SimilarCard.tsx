import { Link } from "react-router";
import type { Similar } from "../../api/types";
import { widthOf } from "../../components/charts/Bars";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { Segmented } from "../../components/ui/Segmented";
import { useFilterSearch } from "../../filters/useFilterSearch";
import { useFilters } from "../../filters/useFilters";
import { athleteName, formatPercent, weightLabel } from "../../format/format";
import styles from "./SimilarCard.module.css";

export function SimilarCard({ similar }: { similar: Similar }) {
  const { setPageParams } = useFilters();
  const search = useFilterSearch();
  const scopes = [
    { value: "weight", label: `Same weight (${weightLabel(similar.weight)})` },
    { value: "all", label: "All weights" },
  ];
  return (
    <Card
      title="Similar athletes"
      term="Similar athletes"
      sample={similar.sample}
      description={`Athletes of the same gender whose scoring techniques look most like this one's (candidates with at least ${similar.min_scores_athlete} scores): who to study next?`}
    >
      <div className={styles.scope}>
        <Segmented
          legend="Compare with"
          options={scopes}
          value={similar.scope}
          onChange={(value) => setPageParams({ similar: value === "all" ? "all" : null })}
        />
      </div>
      {similar.rows.length ? (
        <div className={styles.cards}>
          {similar.rows.map((row) => (
            <Link key={row.athlete.id} className={styles.card} to={{ pathname: `/athletes/${row.athlete.id}`, search }}>
              <span className={styles.head}>
                <span className={styles.name}>
                  {athleteName(row.athlete)}{" "}
                  <span className="cc">
                    {row.athlete.country_code} {weightLabel(row.weight)}
                  </span>
                </span>
                <span className={`num ${styles.similarity}`}>{formatPercent(row.similarity)}</span>
              </span>
              <span className={styles.meter}>
                <i style={{ width: widthOf(row.similarity ?? 0) }} />
              </span>
              <span className={styles.top}>
                {row.top_techniques.map((technique) => `${technique.name} ${technique.n}`).join(" · ")}
              </span>
              <span className="cc">
                {row.n_scores} scores{row.sample.status === "ok" ? "" : ` · ${row.sample.status} sample`}
              </span>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState>
          No similar athlete with at least {similar.min_scores_athlete} scores
          {similar.scope === "weight" ? " in this weight: try All weights." : "."}
        </EmptyState>
      )}
    </Card>
  );
}
