import { Fragment } from "react";
import { useCounters } from "../../api/hooks";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { AthleteLink, TechniqueLink } from "../../components/ui/links";
import { Loaded } from "../../components/ui/Loaded";
import { sampleState } from "../../components/ui/sample";
import { useFilters } from "../../filters/useFilters";
import { formatDecimal, formatPercent } from "../../format/format";

const SHOWN = 8;

export function CounterCard({ code, name }: { code: string; name: string }) {
  const { filters } = useFilters();
  const counters = useCounters(code, filters);
  return (
    <Loaded query={counters}>
      {(response) => {
        const { specialists, conceded, rows } = response.data;
        return (
          <Card
            title="Counter"
            term="Counter"
            sample={specialists.sample}
            description={`What scores against the specialists of ${name}, compared with what usually scores in the same weights. A lift above 1: it scores against them more often than usual.`}
          >
            {specialists.n > 0 ? (
              <>
                <p>
                  {specialists.n} specialist{specialists.n === 1 ? "" : "s"} (main technique, ≥{" "}
                  {formatPercent(specialists.share_threshold)} of their scores) conceded {conceded.n} scores:{" "}
                  {specialists.athletes.map((specialist, index) => (
                    <Fragment key={specialist.athlete.id}>
                      {index > 0 && ", "}
                      <AthleteLink athlete={specialist.athlete} />
                    </Fragment>
                  ))}
                  .
                </p>
                {rows.length === 0 ? (
                  <p>They conceded no score with these filters.</p>
                ) : (
                <div className="tw">
                  <table style={{ minWidth: 420 }}>
                    <thead>
                      <tr>
                        <th scope="col">Technique against them</th>
                        <th scope="col" className="r">n</th>
                        <th scope="col" className="r">Share</th>
                        <th scope="col" className="r">Usual share</th>
                        <th scope="col" className="r">Lift</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.slice(0, SHOWN).map((row) => (
                        <tr key={row.technique?.code ?? "unknown"} data-sample={sampleState(row.sample)}>
                          <th scope="row">
                            <TechniqueLink technique={row.technique} />
                          </th>
                          <td className="r num">{row.n}</td>
                          <td className="r num">{formatPercent(row.share)}</td>
                          <td className="r num">{formatPercent(row.base_share, 1)}</td>
                          <td className="r num">{formatDecimal(row.lift)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                )}
              </>
            ) : (
              <EmptyState>No specialist of {name} with these filters.</EmptyState>
            )}
          </Card>
        );
      }}
    </Loaded>
  );
}
