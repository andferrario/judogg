import type { AthleteDetail, TechniqueRef } from "../../api/types";
import { ScoreLegend, SideBar, StackedBar } from "../../components/charts/Bars";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { AthleteLink, TechniqueLink } from "../../components/ui/links";
import { formatPercent, formatTimeBin, SIDE_LABEL, VALUE_LABEL, weightLabel } from "../../format/format";

type DetailProps = { detail: AthleteDetail };

// The longest bar takes 80% of its cell: room is left for the count next to it.
const LONGEST_BAR = 0.8;

export function videoGroupId(technique: TechniqueRef | null): string {
  return `videos-${technique?.code ?? "unknown"}`;
}

function openVideoGroup(technique: TechniqueRef | null): void {
  const group = document.getElementById(videoGroupId(technique));
  if (group instanceof HTMLDetailsElement) {
    group.open = true;
    group.scrollIntoView?.({ block: "start" });
  }
}

export function AthleteTechniquesCard({ detail }: DetailProps) {
  const max = Math.max(1, ...detail.techniques.map((row) => row.n));
  return (
    <Card
      title="Techniques"
      sample={detail.sample}
      right={<ScoreLegend />}
      description="Every technique this athlete scored with, whole career: what is their game? Each one's share of their scores, how it scores and to which side."
    >
      {detail.techniques.length ? (
        <div className="tw">
          <table style={{ minWidth: 760 }}>
            <thead>
              <tr>
                <th scope="col">Technique</th>
                <th scope="col">Scores</th>
                <th scope="col" className="r">% of their scores</th>
                <th scope="col" className="r">% ippon</th>
                <th scope="col" className="r">% waza-ari</th>
                <th scope="col" className="r">% yuko</th>
                <th scope="col" style={{ textAlign: "center" }}>Left ← → Right</th>
                <th scope="col">Videos</th>
              </tr>
            </thead>
            <tbody>
              {detail.techniques.map((row) => {
                const name = row.technique?.name ?? "Unknown technique";
                return (
                  <tr key={row.technique?.code ?? "unknown"}>
                    <th scope="row">
                      <TechniqueLink technique={row.technique} />
                      <span className="fam">{row.technique ? (row.technique.group_label ?? "") : "no technique tag"}</span>
                    </th>
                    <td style={{ width: "24%" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <StackedBar
                          counts={row.counts}
                          fraction={(row.n / max) * LONGEST_BAR}
                          tip={`Ippon ${row.counts.ippon} · Waza-ari ${row.counts.waza_ari} · Yuko ${row.counts.yuko}`}
                        />
                        <span className="num">{row.n}</span>
                      </div>
                    </td>
                    <td className="r num">{formatPercent(row.share_of_total)}</td>
                    <td className="r num">{formatPercent(row.pct.ippon)}</td>
                    <td className="r num">{formatPercent(row.pct.waza_ari)}</td>
                    <td className="r num">{formatPercent(row.pct.yuko)}</td>
                    <td>
                      <SideBar side={row.side} />
                    </td>
                    <td>
                      <button
                        type="button"
                        className="link-button"
                        aria-label={`${row.n} ${row.n === 1 ? "video" : "videos"} of ${name}`}
                        onClick={() => openVideoGroup(row.technique)}
                      >
                        {row.n} ↓
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState>No scores in the database for this athlete.</EmptyState>
      )}
    </Card>
  );
}

export function VideosCard({ detail }: DetailProps) {
  return (
    <Card
      id="videos"
      title="Videos by technique"
      description="All their scores grouped by technique, to study how they do each one: the links open the contest on JudoBase and JudoTV (JudoBase has buttons to jump to each score)."
    >
      {detail.score_groups.length ? (
        detail.score_groups.map((group, index) => (
          <details key={videoGroupId(group.technique)} id={videoGroupId(group.technique)} open={index === 0} className="video-group">
            <summary>
              {group.technique?.name ?? "Unknown technique"}{" "}
              <span className="cc">
                {group.n} score{group.n === 1 ? "" : "s"}
              </span>
            </summary>
            <div className="tw">
              <table className="nowrap" style={{ minWidth: 820 }}>
                <thead>
                  <tr>
                    <th scope="col">Date</th>
                    <th scope="col">Competition</th>
                    <th scope="col">Weight</th>
                    <th scope="col">Opponent</th>
                    <th scope="col">Score</th>
                    <th scope="col">Side</th>
                    <th scope="col" className="r">When</th>
                    <th scope="col">Video</th>
                  </tr>
                </thead>
                <tbody>
                  {group.rows.map((row, rowIndex) => (
                    <tr key={`${row.contest_code}-${rowIndex}`}>
                      <td className="num">{row.date}</td>
                      <td className="wrap">{row.competition.name}</td>
                      <td className="num">{weightLabel(row.weight)}</td>
                      <td>
                        <AthleteLink athlete={row.opponent} />
                      </td>
                      <td>
                        <strong>{VALUE_LABEL[row.score_value]}</strong>
                        {row.is_awasete && <span className="cc"> awasete</span>}
                      </td>
                      <td>{SIDE_LABEL[row.direction]}</td>
                      <td className="r num">{formatTimeBin(row.time_bin, row.is_gs)}</td>
                      <td>
                        <span className="video-links">
                          <a href={row.judobase_url} target="_blank" rel="noopener noreferrer">
                            JudoBase ↗
                          </a>
                          {row.judotv_url && (
                            <a href={row.judotv_url} target="_blank" rel="noopener noreferrer">
                              JudoTV ↗
                            </a>
                          )}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        ))
      ) : (
        <EmptyState>No scores to watch.</EmptyState>
      )}
    </Card>
  );
}
