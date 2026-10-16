import type { TechniqueDetailResponse } from "../../api/types";
import { HBar, MiniSide, ScoreLegend, SideLegend } from "../../components/charts/Bars";
import { ColumnChart } from "../../components/charts/ColumnChart";
import { LineChart } from "../../components/charts/LineChart";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { sampleState } from "../../components/ui/sample";
import { formatDecimal, formatPercent, weightLabel } from "../../format/format";
import styles from "./ProfileCards.module.css";

type DetailProps = { detail: TechniqueDetailResponse };

export function ByWeightCard({ detail }: DetailProps) {
  const rows = detail.data.by_weight;
  const max = Math.max(0.01, ...rows.map((row) => row.share ?? 0));
  return (
    <Card
      title="By weight"
      sample={detail.data.sample}
      right={<SideLegend />}
      description={`${detail.data.technique.name}'s share of each weight's scores, and the side it is done to: in which categories does it work best?`}
    >
      <ul className={styles.weights}>
        {rows.map((row) => (
          <li key={row.weight.code} data-sample={sampleState(row.sample)}>
            <span className="num">{weightLabel(row.weight)}</span>
            <HBar
              fraction={(row.share ?? 0) / max}
              tip={`${weightLabel(row.weight)}: ${row.n} of ${row.total} scores (${formatPercent(row.share, 1)})`}
            />
            <span className="num">{formatPercent(row.share, 1)}</span>
            <MiniSide side={row.side} />
          </li>
        ))}
      </ul>
    </Card>
  );
}

export function TechniqueTimingCard({ detail }: DetailProps) {
  const name = detail.data.technique.name;
  return (
    <Card
      title="When it scores"
      sample={detail.data.sample}
      right={<ScoreLegend />}
      description={`When in the contest ${name} scores, per 30-second block, golden score apart. Counts, not rates.`}
    >
      <ColumnChart bins={detail.data.timing} label={`Scores with ${name} per 30-second block`} />
    </Card>
  );
}

export function TechniqueTrendCard({ detail }: DetailProps) {
  const { trend, technique } = detail.data;
  return (
    <Card
      title="Trend"
      sample={trend.sample}
      description="Each year's share of the scores: is the technique rising or falling? Dashed lines mark a ruleset change; with fewer than 3 years there is no trend to read."
    >
      {trend.points.length ? (
        <LineChart
          points={trend.points}
          rulesetChanges={trend.ruleset_changes}
          label={`Share of the scores with ${technique.name} per year`}
        />
      ) : (
        <EmptyState>No score with this technique in these years.</EmptyState>
      )}
    </Card>
  );
}

export function CountriesCard({ detail }: DetailProps) {
  const { rows, min_scores_country: minimum } = detail.data.countries;
  const max = Math.max(1, ...rows.map((row) => row.lift ?? 0));
  return (
    <Card
      title="Countries"
      term="Lift"
      description={`Countries whose athletes score with ${detail.data.technique.name} more (lift above 1) or less (below 1) than expected in the same weights. Only countries with at least ${minimum} scores in the filter.`}
    >
      {rows.length ? (
        <ul className={styles.countries}>
          {rows.map((row) => (
            <li key={row.country_code} data-sample={sampleState(row.sample)}>
              <span className="num">{row.country_code}</span>
              <HBar
                fraction={(row.lift ?? 0) / max}
                tip={`${row.country_code}: ${row.n} of ${row.total} scores (${formatPercent(row.share, 1)})`}
              />
              <span className="num">{formatDecimal(row.lift, 1)}</span>
            </li>
          ))}
        </ul>
      ) : (
        <EmptyState>No country with at least {minimum} scores in the filter.</EmptyState>
      )}
    </Card>
  );
}
