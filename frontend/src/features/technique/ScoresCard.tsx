import { useTechniqueScores } from "../../api/hooks";
import { Card } from "../../components/ui/Card";
import { ChipToggle } from "../../components/ui/ChipToggle";
import { EmptyState } from "../../components/ui/EmptyState";
import { AthleteLink } from "../../components/ui/links";
import { Loaded } from "../../components/ui/Loaded";
import { Pagination } from "../../components/ui/Pagination";
import { listParam } from "../../filters/filters";
import { useFilters } from "../../filters/useFilters";
import { formatCount, formatTimeBin, SIDE_LABEL, VALUE_LABEL, weightLabel } from "../../format/format";
import { toggleScoreValue } from "./scoreValues";

const PAGE_SIZE = "10";
const VALUES = ["ippon", "waza_ari", "yuko"] as const;

export function ScoresCard({ code }: { code: string }) {
  const { filters, params, setPageParams } = useFilters();
  const selected = listParam(params, "v_score");
  const page = params.get("v_page") ?? "1";
  const scores = useTechniqueScores(code, filters, {
    score_value: selected.length ? selected.join(",") : undefined,
    page,
    page_size: PAGE_SIZE,
  });
  const toggle = (value: string) => {
    const next = toggleScoreValue(selected, value);
    if (next !== null) setPageParams({ v_score: next.join(","), v_page: null });
  };
  return (
    <Loaded query={scores}>
      {(response) => {
        const list = response.data;
        const pages = Math.max(1, Math.ceil(list.total / list.page_size));
        return (
          <Card
            id="scores"
            title="Scores"
            right={<span className="num">{formatCount(list.total)} results</span>}
            description="Every score with this technique, newest first, with links to the contest on JudoBase and JudoTV (JudoBase has buttons to jump to each score)."
          >
            <div className="chips-row">
              {VALUES.map((value) => (
                <ChipToggle
                  key={value}
                  text
                  pressed={selected.length === 0 || selected.includes(value)}
                  locked={selected.length === 1 && selected[0] === value}
                  tip={selected.length === 1 && selected[0] === value ? "At least one value stays on" : undefined}
                  onClick={() => toggle(value)}
                >
                  {VALUE_LABEL[value]}
                </ChipToggle>
              ))}
            </div>
            {list.rows.length ? (
              <>
                <div className="tw">
                  <table className="nowrap" style={{ minWidth: 900 }}>
                    <thead>
                      <tr>
                        <th scope="col">Date</th>
                        <th scope="col">Competition</th>
                        <th scope="col">Weight</th>
                        <th scope="col">Athlete → opponent</th>
                        <th scope="col">Score</th>
                        <th scope="col">Side</th>
                        <th scope="col" className="r">When</th>
                        <th scope="col">Video</th>
                      </tr>
                    </thead>
                    <tbody>
                      {list.rows.map((row, index) => (
                        <tr key={`${row.contest_code}-${row.athlete.id}-${index}`}>
                          <td className="num">{row.date}</td>
                          <td className="wrap">{row.competition.name}</td>
                          <td className="num">{weightLabel(row.weight)}</td>
                          <td>
                            <AthleteLink athlete={row.athlete} /> <span className="dim">→</span>{" "}
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
                <Pagination
                  page={list.page}
                  pages={pages}
                  onPage={(next) => setPageParams({ v_page: next === 1 ? null : String(next) })}
                />
              </>
            ) : (
              <EmptyState>No scores with these filters.</EmptyState>
            )}
          </Card>
        );
      }}
    </Loaded>
  );
}
