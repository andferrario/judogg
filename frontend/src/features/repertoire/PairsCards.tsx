import type { UseQueryResult } from "@tanstack/react-query";
import { Link, useLocation } from "react-router";
import type { RepertoirePairsResponse } from "../../api/types";
import { useMetaData } from "../../app/meta";
import { DivergingLegend, divergingFill, Heatmap, NEUTRAL_FILL, type HeatRow } from "../../components/charts/Heatmap";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { Loaded } from "../../components/ui/Loaded";
import { sampleState } from "../../components/ui/sample";
import { filterSearch } from "../../filters/filters";
import { formatDecimal, formatPercent } from "../../format/format";

type PairsProps = { query: UseQueryResult<RepertoirePairsResponse> };

function usePairSearch() {
  const params = new URLSearchParams(useLocation().search);
  return (technique: string, companion: string) => filterSearch(params, { technique, with: companion });
}

export function FrequentPairsCard({ query }: PairsProps) {
  const { thresholds } = useMetaData();
  const pairSearch = usePairSearch();
  const minimum = thresholds.athlete_sample_small;
  return (
    <Loaded query={query}>
      {(response) => (
        <Card
          title="Frequent pairs"
          sample={response.data.sample}
          description={`Pairs of techniques that the same athletes score with, at least ${minimum} athletes in common, strongest link first. Support: share of the eligible athletes with both; confidence: share of those with the first who also have the second.`}
        >
          {response.data.pairs.length ? (
            <div className="tw">
              <table style={{ minWidth: 560 }}>
                <thead>
                  <tr>
                    <th scope="col">If they score with</th>
                    <th scope="col">they also score with</th>
                    <th scope="col" className="r">Athletes</th>
                    <th scope="col" className="r">Support</th>
                    <th scope="col" className="r">Confidence</th>
                    <th scope="col" className="r">Lift</th>
                  </tr>
                </thead>
                <tbody>
                  {response.data.pairs.map((pair) => (
                    <tr key={`${pair.a.code}-${pair.b.code}`} data-sample={sampleState(pair.sample)}>
                      <th scope="row">
                        <Link
                          replace
                          className="tlink"
                          to={{ pathname: "/repertoire", search: pairSearch(pair.a.code, pair.b.code) }}
                        >
                          {pair.a.name}
                        </Link>
                      </th>
                      <td>{pair.b.name}</td>
                      <td className="r num">{pair.n_both}</td>
                      <td className="r num">{formatPercent(pair.support, 1)}</td>
                      <td className="r num">{formatPercent(pair.confidence)}</td>
                      <td className="r num">{formatDecimal(pair.lift)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState>No pair with at least {minimum} athletes in common.</EmptyState>
          )}
        </Card>
      )}
    </Loaded>
  );
}

export function LiftMatrixCard({ query }: PairsProps) {
  const { thresholds } = useMetaData();
  const pairSearch = usePairSearch();
  return (
    <Loaded query={query}>
      {(response) => {
        const { techniques, cells } = response.data.matrix;
        const rows: HeatRow[] = techniques.map((first, i) => ({
          key: first.code,
          label: first.name,
          dimmed: false,
          cells: techniques.map((second, j) => {
            const cell = cells[i]?.[j] ?? null;
            if (cell === null) return null;
            const weak = cell.sample.status === "insufficient";
            const tip = `${first.name} + ${second.name}\nlift ${formatDecimal(cell.lift)} · ${cell.n_both} athletes with both`;
            return {
              key: second.code,
              text: weak ? "·" : formatDecimal(cell.lift, 1),
              fill: weak ? NEUTRAL_FILL : divergingFill(cell.lift),
              tip,
              label: tip.replace("\n", ": "),
              to: { pathname: "/repertoire", search: pairSearch(first.code, second.code) },
            };
          }),
        }));
        return (
          <Card
            title="Lift matrix"
            sample={response.data.sample}
            right={<DivergingLegend />}
            description={`The lift of every pair among the ${techniques.length} techniques most common in repertoires: above 1 (blue) they are scored together more often than expected, below 1 (red) less. "·" = fewer than ${thresholds.athlete_sample_small} athletes with both; a cell opens the pair.`}
          >
            {techniques.length > 1 ? (
              <Heatmap
                columns={techniques.map((technique) => ({ key: technique.code, label: technique.name }))}
                rows={rows}
                rowHeadWidth={130}
                replace
              />
            ) : (
              <EmptyState>Not enough techniques in the repertoires.</EmptyState>
            )}
          </Card>
        );
      }}
    </Loaded>
  );
}
