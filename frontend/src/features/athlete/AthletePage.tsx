import { useParams } from "react-router";
import { useAthlete } from "../../api/hooks";
import type { AthleteDetail } from "../../api/types";
import { PageContent } from "../../app/PageFrame";
import { AthleteTechniquesCard, VideosCard } from "./AthleteCards";
import { SimilarCard } from "./SimilarCard";
import { ErrorBox } from "../../components/ui/ErrorBox";
import { Kpi, KpiGrid } from "../../components/ui/Kpi";
import { BackToTechniques, TechniqueLink } from "../../components/ui/links";
import { PageHeader } from "../../components/ui/PageHeader";
import { Skeleton } from "../../components/ui/Skeleton";
import { Warnings } from "../../components/ui/Warnings";
import { useFilters } from "../../filters/useFilters";
import { athleteName, formatCount, formatPercent, weightLabel } from "../../format/format";

const NOTE = "Whole career in the database, not filtered. Results and contest list: JudoBase.";

export function AthletePage() {
  const { id = "" } = useParams();
  const { params } = useFilters();
  // Not filtered: only the page's own parameters reach the API, the filters stay in the URL for the other pages.
  const athlete = useAthlete(id, {
    similar_scope: params.get("similar") === "all" ? "all" : "weight",
    min_scores_athlete: params.get("min_scores_athlete") ?? undefined,
  });
  if (athlete.isError) {
    return (
      <>
        <PageHeader title="Judoka" big back={<BackToTechniques />} />
        <ErrorBox error={athlete.error} onRetry={() => void athlete.refetch()} retrying={athlete.isFetching} />
      </>
    );
  }
  if (athlete.data === undefined) {
    return (
      <>
        <PageHeader title="Judoka" big back={<BackToTechniques />} />
        <Skeleton />
      </>
    );
  }
  const detail = athlete.data.data;
  return (
    <>
      <PageHeader
        title={athleteName(detail.athlete)}
        big
        back={<BackToTechniques />}
        summary={<AthleteSummary detail={detail} />}
        note={NOTE}
      />
      <Warnings warnings={athlete.data.warnings} />
      <PageContent refreshing={athlete.isPlaceholderData}>
        <AthleteKpis detail={detail} />
        <AthleteTechniquesCard detail={detail} />
        {/* A new athlete starts with their own first group open, not with the previous athlete's groups. */}
        <VideosCard key={detail.athlete.id} detail={detail} />
        <SimilarCard similar={detail.similar} />
      </PageContent>
    </>
  );
}

function AthleteSummary({ detail }: { detail: AthleteDetail }) {
  const { from, to } = detail.years;
  return (
    <>
      <span className="num">{detail.athlete.country_code}</span>
      {detail.weights.map((item) => (
        <span key={item.weight.code}>
          {" · "}
          {weightLabel(item.weight)} <span className="cc">{item.contests} contests</span>
        </span>
      ))}
      {" · "}
      {from === to ? from : `${from}–${to}`}
      {" · "}
      <a href={detail.judobase_url} target="_blank" rel="noopener noreferrer">
        JudoBase profile ↗
      </a>
    </>
  );
}

function AthleteKpis({ detail }: { detail: AthleteDetail }) {
  const kpis = detail.kpis;
  return (
    <KpiGrid>
      <Kpi
        label="Scores"
        term="Score"
        value={formatCount(kpis.scores)}
        sub={`in ${formatCount(kpis.contests)} contests · ${kpis.competitions} competition${kpis.competitions === 1 ? "" : "s"}`}
      />
      <Kpi label="Different techniques" value={formatCount(kpis.techniques)} sub="scored with at least once" />
      <Kpi label="Ippon share" value={formatPercent(kpis.ippon_share)} sub="of all their scores" />
      <Kpi
        label="Main technique"
        value={
          kpis.main_technique ? (
            <span className="kpi-text">
              <TechniqueLink technique={kpis.main_technique} />
            </span>
          ) : (
            "–"
          )
        }
        sub="most scores"
        small
      />
    </KpiGrid>
  );
}
