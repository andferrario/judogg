import { useMetaData } from "../../app/meta";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { Kpi, KpiGrid } from "../../components/ui/Kpi";
import { PageHeader } from "../../components/ui/PageHeader";
import { formatCount, formatPercent } from "../../format/format";
import styles from "./CoveragePage.module.css";

const LEVEL_LABEL = { elite: "Elite", continental: "Continental" } as const;

const ISSUE_LABEL: Record<string, string> = {
  summary_mismatch: "IJF totals do not match the events",
  unknown_event_type: "Unknown event type (ignored)",
  new_tag_group: "Technique without a family",
  unknown_weight: "Unknown weight category (skipped)",
  unknown_actor: "Event assigned to an athlete not in the contest (ignored)",
  no_events: "Contest without events (skipped)",
};

export function CoveragePage() {
  const meta = useMetaData();
  const { totals, competitions, excluded } = meta.coverage;
  const rulesetLabel = (id: number) => meta.rulesets.find((ruleset) => ruleset.id === id)?.label ?? String(id);
  const weight = (code: string) => {
    const option = meta.weights.find((item) => item.code === code);
    return option ? `${option.label}${option.gender === "m" ? "M" : "W"}` : code;
  };
  return (
    <>
      <PageHeader title="Coverage" summary="What is in the database. Not affected by the filters." />
      <KpiGrid>
        <Kpi label="Competitions" value={formatCount(totals.competitions)} sub="included in every analysis" />
        <Kpi label="Contests" value={formatCount(totals.contests)} sub="individual senior contests" />
        <Kpi label="Scores" value={formatCount(totals.scores)} sub="ippon, waza-ari and yuko" />
        <Kpi label="Penalties" value={formatCount(totals.penalties)} sub="shidos and hansoku-make" />
        <Kpi label="Athletes" value={formatCount(totals.athletes)} sub="with at least one contest" />
        <Kpi
          label="Scores from continental competitions"
          value={formatPercent(totals.continental_score_share)}
          sub="above 10% a level filter would be needed"
        />
      </KpiGrid>

      <Card
        title="Competitions loaded"
        description="The competitions behind every number of the app, with their level, ruleset and the share of their scores that has a technique tag. A competition can be loaded for some categories only."
      >
        <div className="tw">
          <table style={{ minWidth: 820 }}>
            <thead>
              <tr>
                <th scope="col">Competition</th>
                <th scope="col">Dates</th>
                <th scope="col">Rank</th>
                <th scope="col">Level</th>
                <th scope="col">Ruleset</th>
                <th scope="col" className="r">Tagged scores</th>
                <th scope="col" className="r">Contests</th>
                <th scope="col">Categories</th>
              </tr>
            </thead>
            <tbody>
              {competitions.map((competition) => (
                <tr key={competition.id}>
                  <th scope="row">{competition.name}</th>
                  <td className="num">
                    {competition.date_from} → {competition.date_to}
                  </td>
                  <td>{competition.rank_name}</td>
                  <td>{LEVEL_LABEL[competition.level]}</td>
                  <td>{rulesetLabel(competition.ruleset_id)}</td>
                  <td className="r num">{formatPercent(competition.tag_coverage)}</td>
                  <td className="r num">{formatCount(competition.contests)}</td>
                  <td>
                    <div className={styles.chips}>
                      {competition.by_weight.map((item) => (
                        <span key={item.weight} className="chip-static" data-tip={`${item.contests} contests`}>
                          {weight(item.weight)}
                          <span className="sr"> {item.contests} contests</span>
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="grid2">
        <Card
          title="Data quality"
          description="Contests whose IJF data is inconsistent or incomplete: they are flagged where they appear, or skipped when they cannot be read."
        >
          {meta.quality_issues.length ? (
            <table>
              <thead>
                <tr>
                  <th scope="col">Issue</th>
                  <th scope="col" className="r">Contests</th>
                </tr>
              </thead>
              <tbody>
                {meta.quality_issues.map((issue) => (
                  <tr key={issue.code}>
                    <th scope="row">{ISSUE_LABEL[issue.code] ?? issue.code}</th>
                    <td className="r num">{formatCount(issue.contests)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState>No known issue.</EmptyState>
          )}
        </Card>
        <Card
          title="Excluded competitions"
          description="Competitions never analysed, with the reason: not individual senior judo with standard rules (kata, teams, para, deaf…), or data without events or technique tags. Inclusion depends on the data, not on the level."
        >
          {excluded.length === 0 ? (
            <EmptyState>No competition excluded.</EmptyState>
          ) : (
            <details>
              <summary className="link-button">{excluded.length} competitions excluded</summary>
              <div className={`tw ${styles.excluded}`}>
                <table>
                  <thead>
                    <tr>
                      <th scope="col">Year</th>
                      <th scope="col">Competition</th>
                      <th scope="col">Level</th>
                      <th scope="col">Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {excluded.map((competition) => (
                      <tr key={competition.id}>
                        <td className="num">{competition.year}</td>
                        <td>{competition.name}</td>
                        <td>{LEVEL_LABEL[competition.level]}</td>
                        <td className="dim">{competition.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </details>
          )}
        </Card>
      </div>

      <Card title="Glossary" description="Every term used in the app, with its definition and the limits of the data.">
        <table>
          <tbody>
            {meta.glossary.map((entry) => (
              <tr key={entry.term}>
                <th scope="row" className={styles.term}>
                  {entry.term}
                </th>
                <td>{entry.definition}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </>
  );
}
