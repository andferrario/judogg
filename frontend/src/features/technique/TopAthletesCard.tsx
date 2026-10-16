import type { TechniqueDetailResponse } from "../../api/types";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { AthleteLink } from "../../components/ui/links";
import { formatPercent, weightLabel } from "../../format/format";

export function TopAthletesCard({ detail }: { detail: TechniqueDetailResponse }) {
  const name = detail.data.technique.name;
  return (
    <Card
      title="Top athletes"
      description={`The athletes who score most with ${name}, and how much of their own scoring it is: a high percentage marks a specialist.`}
    >
      {detail.data.top_athletes.length === 0 ? (
        <EmptyState>No athlete with these filters.</EmptyState>
      ) : (
        <div className="tw">
          <table style={{ minWidth: 620 }}>
            <thead>
              <tr>
                <th scope="col">Athlete</th>
                <th scope="col">Weight</th>
                <th scope="col" className="r">Scores</th>
                <th scope="col" className="r">Ippon</th>
                <th scope="col" className="r">% of their scores</th>
                <th scope="col">Side</th>
                <th scope="col">Profile</th>
              </tr>
            </thead>
            <tbody>
              {detail.data.top_athletes.map((row) => (
                <tr key={row.athlete.id}>
                  <th scope="row">
                    <AthleteLink athlete={row.athlete} />
                  </th>
                  <td className="num">{weightLabel(row.weight)}</td>
                  <td className="r num">{row.n}</td>
                  <td className="r num">{row.n_ippon}</td>
                  <td className="r num">
                    {formatPercent(row.share_of_total)} <span className="cc">of {row.total_scores}</span>
                  </td>
                  <td className="num">
                    L {row.side.left} · R {row.side.right}
                    {row.side.unknown > 0 && ` · ? ${row.side.unknown}`}
                  </td>
                  <td>
                    <a href={row.judobase_url} target="_blank" rel="noopener noreferrer">
                      JudoBase ↗
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
