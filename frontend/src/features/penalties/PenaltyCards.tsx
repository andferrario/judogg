import { useLocation } from "react-router";
import type { PenaltiesResponse } from "../../api/types";
import { HBar, SplitBar } from "../../components/charts/Bars";
import { ColumnChart } from "../../components/charts/ColumnChart";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { Kpi, KpiGrid } from "../../components/ui/Kpi";
import { sampleState } from "../../components/ui/sample";
import { formatCount, formatDecimal, formatPercent, weightLabel } from "../../format/format";

type ResponseProps = { response: PenaltiesResponse };

// The longest bar takes 80% of its cell: room is left for the share next to it.
const LONGEST_BAR = 0.8;

export function PenaltyKpis({ response }: ResponseProps) {
  const kpis = response.data.kpis;
  return (
    <KpiGrid>
      <Kpi label="Shido" value={formatCount(kpis.n_shido)} sub={`${formatCount(kpis.n_penalties)} penalties in total`} />
      <Kpi
        label="Shido / contest"
        value={formatDecimal(kpis.shido_per_contest)}
        sub={`${formatCount(kpis.played_contests)} contests fought`}
      />
      <Kpi
        label="Hansoku-make"
        value={formatPercent(kpis.hansoku_share, 1)}
        sub="contests decided by the 3rd shido"
      />
    </KpiGrid>
  );
}

export function ReasonsCard({ response }: ResponseProps) {
  const highlighted = new URLSearchParams(useLocation().search).get("reason");
  const reasons = response.data.reasons;
  const max = Math.max(0.01, ...reasons.map((row) => row.share ?? 0));
  return (
    <Card
      title="Shido reasons"
      sample={response.data.sample}
      description="What the shidos are given for: each reason's share of the penalties, and how often it was the deciding one (the third shido, which gives hansoku-make). Reasons as tagged by the IJF."
    >
      {reasons.length === 0 ? (
        <EmptyState>{NO_PENALTY}</EmptyState>
      ) : (
      <div className="tw">
        <table style={{ minWidth: 640 }}>
          <thead>
            <tr>
              <th scope="col">Reason</th>
              <th scope="col">Share of penalties</th>
              <th scope="col" className="r">n</th>
              <th scope="col" className="r">Deciding</th>
              <th scope="col" className="r">% deciding</th>
            </tr>
          </thead>
          <tbody>
            {reasons.map((row) => (
              <tr
                key={row.reason?.code ?? "none"}
                data-sample={sampleState(row.sample)}
                data-selected={(row.reason !== null && row.reason.code === highlighted) || undefined}
              >
                <th scope="row">
                  {row.reason ? row.reason.name : <span className="dim">No reason tagged</span>}
                  <span className="fam">{row.reason?.group_label ?? ""}</span>
                </th>
                <td style={{ width: "38%" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <HBar
                      tone="penalty"
                      fraction={((row.share ?? 0) / max) * LONGEST_BAR}
                      tip={`${row.n} of ${formatCount(response.data.kpis.n_penalties)} penalties`}
                    />
                    <span className="num">{formatPercent(row.share, 1)}</span>
                  </div>
                </td>
                <td className="r num">{formatCount(row.n)}</td>
                <td className="r num">{formatCount(row.n_deciding)}</td>
                <td className="r num">{formatPercent(row.deciding_share)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      )}
    </Card>
  );
}

const NO_PENALTY = "No penalty with these filters. Widen the filters.";
const ORDINAL = ["1st", "2nd", "3rd"];

export function GroupsCard({ response }: ResponseProps) {
  return (
    <Card
      title="By group"
      description="Shido reasons grouped by kind: is the referee mostly punishing passivity, grip fighting or infractions?"
    >
      {response.data.by_group.length === 0 ? (
        <EmptyState>{NO_PENALTY}</EmptyState>
      ) : (
      <SplitBar
        parts={response.data.by_group.map((group) => ({
          key: group.group_label ?? "none",
          label: group.group_label ?? "No reason",
          n: group.n,
          share: group.share,
        }))}
      />
      )}
    </Card>
  );
}

export function PenaltyTimingCard({ response }: ResponseProps) {
  return (
    <Card
      title="When shidos happen"
      sample={response.data.sample}
      description="Penalties per 30-second block of regulation time, golden score apart: when do referees give shidos? Counts, not rates: more contests reach 3:00 than golden score."
    >
      <ColumnChart bins={response.data.timing} label="Penalties per 30-second block" />
    </Card>
  );
}

export function PenaltyWeightsCard({ response }: ResponseProps) {
  return (
    <Card
      title="By weight"
      description="Shidos per contest and the share of contests decided by the third shido in each weight: where is the fight most penalised? Contests actually fought only."
    >
      <div className="tw">
        <table style={{ minWidth: 420 }}>
          <thead>
            <tr>
              <th scope="col">Weight</th>
              <th scope="col" className="r">Contests</th>
              <th scope="col" className="r">Shido / contest</th>
              <th scope="col" className="r">Hansoku-make</th>
            </tr>
          </thead>
          <tbody>
            {response.data.by_weight.map((row) => (
              <tr key={row.weight.code} data-sample={sampleState(row.sample)}>
                <th scope="row" className="num">
                  {weightLabel(row.weight)}
                </th>
                <td className="r num">{formatCount(row.contests)}</td>
                <td className="r num">{formatDecimal(row.shido_per_contest)}</td>
                <td className="r num">{formatPercent(row.hansoku_share, 1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

export function ShidoNumberCard({ response }: ResponseProps) {
  return (
    <Card
      title="1st, 2nd, 3rd shido"
      description="The main reasons of the first, second and third shido of a contest: does the reason change as the contest goes on? The third gives hansoku-make."
    >
      <div className="shido-numbers">
        {response.data.by_number.map((number) => (
          <div key={number.number} data-sample={sampleState(number.sample)}>
            <h3>
              {ORDINAL[number.number - 1]} shido · {formatCount(number.n)}
            </h3>
            {number.reasons.length === 0 && <p className="dim">none</p>}
            <ul>
              {number.reasons.map((row) => (
                <li key={row.reason?.code ?? "none"}>
                  <span>{row.reason ? row.reason.name : <span className="dim">No reason</span>}</span>
                  <span className="num">{formatPercent(row.share)}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </Card>
  );
}
