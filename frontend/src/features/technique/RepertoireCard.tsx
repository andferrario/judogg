import { Link } from "react-router";
import { useRepertoire } from "../../api/hooks";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { TechniqueLink } from "../../components/ui/links";
import { Loaded } from "../../components/ui/Loaded";
import { sampleState } from "../../components/ui/sample";
import { useFilterSearch } from "../../filters/useFilterSearch";
import { useFilters } from "../../filters/useFilters";
import { formatDecimal, formatPercent } from "../../format/format";

const SHOWN = 8;

export function RepertoireCard({ code, name }: { code: string; name: string }) {
  const { filters } = useFilters();
  const repertoireSearch = useFilterSearch({ technique: code });
  const repertoire = useRepertoire(code, filters);
  return (
    <Loaded query={repertoire}>
      {(response) => {
        const { cohort, companions } = response.data;
        return (
          <Card
            title="Repertoire"
            term="Repertoire"
            sample={cohort.sample}
            description={`Athletes who score with ${name}: which other techniques do they also score with, and how much more often than expected?`}
          >
            {companions.length ? (
              <>
                <p>
                  {cohort.with_technique} of {cohort.eligible} eligible athletes have {name} in their repertoire.
                </p>
                <div className="tw">
                  <table style={{ minWidth: 420 }}>
                    <thead>
                      <tr>
                        <th scope="col">They also score with</th>
                        <th scope="col" className="r">Athletes</th>
                        <th scope="col" className="r">% of them</th>
                        <th scope="col" className="r">Lift</th>
                      </tr>
                    </thead>
                    <tbody>
                      {companions.slice(0, SHOWN).map((companion) => (
                        <tr key={companion.technique.code} data-sample={sampleState(companion.sample)}>
                          <th scope="row">
                            <TechniqueLink technique={companion.technique} />
                          </th>
                          <td className="r num">{companion.n_both}</td>
                          <td className="r num">{formatPercent(companion.p_given)}</td>
                          <td className="r num">{formatDecimal(companion.lift)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="more">
                  <Link className="btn" to={{ pathname: "/repertoire", search: repertoireSearch }}>
                    Open in Repertoire
                  </Link>
                </div>
              </>
            ) : (
              <EmptyState>
                No eligible athlete scored at least {response.filters.min_scores_technique} times with {name}. Widen the
                filters or lower the thresholds.
              </EmptyState>
            )}
          </Card>
        );
      }}
    </Loaded>
  );
}
