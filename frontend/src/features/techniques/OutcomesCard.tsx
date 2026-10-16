import { useOutcomes } from "../../api/hooks";
import type { OutcomeRow, TotalOutcomes } from "../../api/types";
import { HBar } from "../../components/charts/Bars";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { Loaded } from "../../components/ui/Loaded";
import { sampleState } from "../../components/ui/sample";
import { useFilters } from "../../filters/useFilters";
import { formatCount, formatDecimal, formatDuration, formatPercent, weightLabel } from "../../format/format";

type EndType = TotalOutcomes["end_types"][number]["end_type"];

// "Ippon" includes the waza-ari awasete ippon, "Hansoku-make" the double one: the groupings the table shows.
function share(row: TotalOutcomes, ...types: EndType[]): number | null {
  const shares = row.end_types.filter((item) => types.includes(item.end_type)).map((item) => item.share);
  return shares.every((value) => value === null) ? null : shares.reduce<number>((sum, value) => sum + (value ?? 0), 0);
}

// Walkovers and withdrawals are contests too: only a filter without any contest is empty.
function isEmpty(total: TotalOutcomes): boolean {
  return total.played + total.walkovers.fusen_gachi + total.walkovers.kiken_gachi === 0;
}

export function OutcomesCard() {
  const { filters } = useFilters();
  const outcomes = useOutcomes(filters);
  return (
    <Loaded query={outcomes}>
      {(response) => (
        <Card
          title="Golden score & outcomes"
          description="How contests end in each weight: how many go to golden score, end by ippon or by the third shido, how long they last. Only contests actually fought: walkovers (fusen-gachi) and withdrawals (kiken-gachi) are counted apart; ippon includes waza-ari awasete ippon."
        >
          {isEmpty(response.data.total) ? (
            <EmptyState>No contest with these filters. Widen the filters.</EmptyState>
          ) : (
            <div className="tw">
              <table style={{ minWidth: 720 }}>
                <thead>
                  <tr>
                    <th scope="col">Weight</th>
                    <th scope="col">To golden score</th>
                    <th scope="col" className="r">Fought</th>
                    <th scope="col" className="r">Ippon</th>
                    <th scope="col" className="r">Hansoku-make</th>
                    <th scope="col" className="r">Shido / contest</th>
                    <th scope="col" className="r">Avg duration</th>
                    <th scope="col" className="r">Walkovers · withdrawals</th>
                  </tr>
                </thead>
                <tbody>
                  {response.data.rows.map((row) => (
                    <OutcomeRowView key={row.weight.code} label={weightLabel(row.weight)} row={row} />
                  ))}
                  <OutcomeRowView label="All" row={response.data.total} total />
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}
    </Loaded>
  );
}

function OutcomeRowView({ label, row, total = false }: { label: string; row: OutcomeRow | TotalOutcomes; total?: boolean }) {
  return (
    <tr data-sample={sampleState(row.sample)} style={total ? { fontWeight: 700 } : undefined}>
      <th scope="row" className="num">
        {label}
      </th>
      <td style={{ width: "24%" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <HBar fraction={row.gs_share ?? 0} />
          <span className="num">{formatPercent(row.gs_share)}</span>
        </div>
      </td>
      <td className="r num">{formatCount(row.played)}</td>
      <td className="r num">{formatPercent(share(row, "ippon", "waza_ari_awasete"))}</td>
      <td className="r num">{formatPercent(share(row, "hansoku_shido", "double_hansoku"))}</td>
      <td className="r num">{formatDecimal(row.shido_per_contest)}</td>
      <td className="r num">{formatDuration(row.avg_duration_s)}</td>
      <td className="r num">
        {row.walkovers.fusen_gachi} · {row.walkovers.kiken_gachi}
      </td>
    </tr>
  );
}
