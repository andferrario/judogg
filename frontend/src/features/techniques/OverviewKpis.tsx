import type { OverviewResponse } from "../../api/types";
import { Kpi, KpiGrid } from "../../components/ui/Kpi";
import { formatCount, formatPercent } from "../../format/format";

export function OverviewKpis({ overview }: { overview: OverviewResponse }) {
  const { kpis, outcomes } = overview.data;
  return (
    <KpiGrid>
      <Kpi
        label="Scores"
        term="Score"
        value={formatCount(kpis.scores)}
        sub="Ippon, waza-ari and yuko: every share on this page is a share of them"
      />
      <Kpi
        label="Contests"
        value={formatCount(kpis.contests)}
        sub={`${formatCount(outcomes.played)} fought · ${formatPercent(kpis.gs_share)} to golden score`}
      />
      <Kpi
        label="Scoring athletes"
        value={formatCount(kpis.scoring_athletes)}
        sub={`athletes with at least one score · ${formatCount(kpis.techniques)} different techniques`}
      />
      <Kpi
        label="Unknown technique"
        term="Unknown technique"
        value={formatPercent(kpis.unknown_technique_share)}
        sub="scores without a technique tag: in the totals, in no technique"
      />
      <Kpi
        label="Unknown side"
        value={formatPercent(kpis.unknown_side_share)}
        sub="scores without a side: left out of the left/right bars"
      />
    </KpiGrid>
  );
}
