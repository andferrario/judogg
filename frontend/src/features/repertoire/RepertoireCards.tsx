import { Link, useLocation } from "react-router";
import type { RepertoireResponse } from "../../api/types";
import { HBar } from "../../components/charts/Bars";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { Kpi, KpiGrid } from "../../components/ui/Kpi";
import { AthleteLink } from "../../components/ui/links";
import { sampleState } from "../../components/ui/sample";
import { filterSearch } from "../../filters/filters";
import { formatCount, formatDecimal, formatPercent, weightLabel } from "../../format/format";

type ResponseProps = { response: RepertoireResponse };

const SHOWN = 12;
// The longest bar takes 78% of its cell: room is left for the share next to it.
const LONGEST_BAR = 0.78;

const scores = (n: number) => `${n} score${n === 1 ? "" : "s"}`;

export function RepertoireIntro({ response }: ResponseProps) {
  const { filters, data } = response;
  return (
    <p className="page-note">
      {data.cohort.eligible} athletes with at least {scores(filters.min_scores_athlete)} · a technique is in an
      athlete's repertoire with at least {scores(filters.min_scores_technique)}. Scores, not attempts: this is “also
      score with”, not combinations within one action.
    </p>
  );
}

export function RepertoireKpis({ response }: ResponseProps) {
  const { filters, data } = response;
  return (
    <KpiGrid>
      <Kpi
        label="Eligible athletes"
        value={formatCount(data.cohort.eligible)}
        sub={`at least ${scores(filters.min_scores_athlete)} in the filter`}
      />
      <Kpi
        label={`With ${data.technique.name}`}
        value={formatCount(data.cohort.with_technique)}
        sub={`at least ${scores(filters.min_scores_technique)} with it: the cohort`}
      />
      <Kpi
        label="Companions"
        value={formatCount(data.companions.length)}
        sub="other techniques in the repertoires of the cohort"
      />
    </KpiGrid>
  );
}

export function CompanionsCard({ response }: ResponseProps) {
  const { search } = useLocation();
  const params = new URLSearchParams(search);
  const { technique, cohort, companions } = response.data;
  const selected = params.get("with");
  const max = Math.max(0.01, ...companions.map((companion) => companion.p_given ?? 0));
  return (
    <Card
      title={`${technique.name} → also score with`}
      term="Lift"
      sample={cohort.sample}
      description={`Athletes with ${technique.name} in their repertoire: which other techniques are in theirs, and how much more often than among all eligible athletes? A row opens the athletes behind it.`}
    >
      {companions.length ? (
        <>
          <div className="tw">
            <table style={{ minWidth: 460 }}>
              <thead>
                <tr>
                  <th scope="col">Technique</th>
                  <th scope="col">% of the cohort</th>
                  <th scope="col" className="r">Athletes</th>
                  <th scope="col" className="r">Usual %</th>
                  <th scope="col" className="r">Lift</th>
                </tr>
              </thead>
              <tbody>
                {companions.slice(0, SHOWN).map((companion) => (
                  <tr
                    key={companion.technique.code}
                    data-sample={sampleState(companion.sample)}
                    data-selected={selected === companion.technique.code || undefined}
                  >
                    <th scope="row">
                      <Link
                        replace
                        className="tlink"
                        to={{
                          pathname: "/repertoire",
                          search: filterSearch(params, { technique: technique.code, with: companion.technique.code }),
                        }}
                      >
                        {companion.technique.name}
                      </Link>
                    </th>
                    <td style={{ width: "38%" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <HBar
                          fraction={((companion.p_given ?? 0) / max) * LONGEST_BAR}
                          tip={`${companion.n_both} of the ${cohort.with_technique} athletes of the cohort`}
                        />
                        <span className="num">{formatPercent(companion.p_given)}</span>
                      </div>
                    </td>
                    <td className="r num">{companion.n_both}</td>
                    <td className="r num">{formatPercent(companion.p_base)}</td>
                    <td className="r num">{formatDecimal(companion.lift)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="card-note">
            Lift = share in the cohort ÷ usual share among the eligible athletes of the same weights. Above 1 the link
            is stronger than the technique's popularity alone.
          </p>
        </>
      ) : (
        <EmptyState>No companion technique with these filters.</EmptyState>
      )}
    </Card>
  );
}

export function PairAthletesCard({ response }: ResponseProps) {
  const { technique, pair_athletes: pair } = response.data;
  return (
    <Card
      title={pair ? `${technique.name} + ${pair.technique.name}` : "Athletes"}
      term="Support"
      description="The athletes who have both techniques in their repertoire, with their scores with each: who to watch for this combination?"
    >
      {pair === null ? (
        <EmptyState>Pick a companion technique to see the athletes behind it.</EmptyState>
      ) : pair.rows.length === 0 ? (
        <EmptyState>No athlete has both techniques in their repertoire.</EmptyState>
      ) : (
        <div className="tw">
          <table style={{ minWidth: 420 }}>
            <thead>
              <tr>
                <th scope="col">Athlete</th>
                <th scope="col">Weight</th>
                <th scope="col" className="r">{technique.name}</th>
                <th scope="col" className="r">{pair.technique.name}</th>
                <th scope="col" className="r">All scores</th>
              </tr>
            </thead>
            <tbody>
              {pair.rows.map((row) => (
                <tr key={row.athlete.id}>
                  <th scope="row">
                    <AthleteLink athlete={row.athlete} />
                  </th>
                  <td className="num">{weightLabel(row.weight)}</td>
                  <td className="r num">{row.n_technique}</td>
                  <td className="r num">{row.n_with}</td>
                  <td className="r num">{row.n_total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
