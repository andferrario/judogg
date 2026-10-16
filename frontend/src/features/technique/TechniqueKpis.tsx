import type { TechniqueDetailResponse } from "../../api/types";
import { Kpi, KpiGrid } from "../../components/ui/Kpi";
import { formatCount, formatPercent } from "../../format/format";

export function TechniqueKpis({ detail }: { detail: TechniqueDetailResponse }) {
  const kpis = detail.data.kpis;
  return (
    <KpiGrid>
      <Kpi
        label="Scores"
        value={formatCount(kpis.n_scores)}
        sub={kpis.rank === null ? "not ranked" : `#${kpis.rank} of ${kpis.of} techniques`}
      />
      <Kpi
        label="Ippon · waza · yuko"
        term="Ippon / waza-ari / yuko breakdown"
        small
        value={`${formatPercent(kpis.pct.ippon)} · ${formatPercent(kpis.pct.waza_ari)} · ${formatPercent(kpis.pct.yuko)}`}
        sub={`overall ippon ${formatPercent(kpis.overall_pct_ippon)} · awasete ${kpis.n_awasete}`}
      />
      <Kpi
        label="Right side"
        value={formatPercent(kpis.right_share)}
        sub={`of known side · unknown ${formatPercent(kpis.unknown_side_share)}`}
      />
      <Kpi label="Athletes" value={formatCount(kpis.n_athletes)} sub="scored with it at least once" />
      <Kpi
        label="In golden score"
        value={formatPercent(kpis.gs_share)}
        sub={`of its scores came in golden score · overall ${formatPercent(kpis.overall_gs_share)}`}
      />
    </KpiGrid>
  );
}
