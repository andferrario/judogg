import { useId } from "react";
import { useNavigate, useParams } from "react-router";
import { useTechnique } from "../../api/hooks";
import type { TechniqueDetailResponse } from "../../api/types";
import { useMetaData } from "../../app/meta";
import { PageFrame } from "../../app/PageFrame";
import { EmptyState } from "../../components/ui/EmptyState";
import { BackToTechniques } from "../../components/ui/links";
import { Notice } from "../../components/ui/Notice";
import { useFilterSearch } from "../../filters/useFilterSearch";
import { useFilters } from "../../filters/useFilters";
import { DOMAIN_LABEL } from "../../format/format";
import { CounterCard } from "./CounterCard";
import { ByWeightCard, CountriesCard, TechniqueTimingCard, TechniqueTrendCard } from "./ProfileCards";
import { RepertoireCard } from "./RepertoireCard";
import { ScoresCard } from "./ScoresCard";
import { TechniqueKpis } from "./TechniqueKpis";
import { TopAthletesCard } from "./TopAthletesCard";

export function TechniquePage() {
  const { code = "" } = useParams();
  const { filters } = useFilters();
  const meta = useMetaData();
  const detail = useTechnique(code, filters);
  const name = meta.techniques.find((technique) => technique.code === code)?.name ?? code;
  return (
    <PageFrame
      title={name}
      big
      query={detail}
      back={<BackToTechniques />}
      aside={<ChangeTechnique code={code} />}
      subtitle={(response) => {
        const technique = response.data.technique;
        return [technique.group_label, technique.domain && DOMAIN_LABEL[technique.domain]].filter(Boolean).join(" · ");
      }}
    >
      {(response) =>
        response.data.kpis.n_scores === 0 ? (
          <EmptyState>No scores with this technique for the current filters. Widen the filters.</EmptyState>
        ) : (
          <TechniqueContent detail={response} />
        )
      }
    </PageFrame>
  );
}

function TechniqueContent({ detail }: { detail: TechniqueDetailResponse }) {
  return (
    <>
      <TechniqueKpis detail={detail} />
      {detail.data.technique.domain === "ground" && <HoldDownNotice />}
      <div className="grid2">
        <ByWeightCard detail={detail} />
        <TechniqueTimingCard detail={detail} />
      </div>
      <div className="grid2">
        <TechniqueTrendCard detail={detail} />
        <CountriesCard detail={detail} />
      </div>
      <TopAthletesCard detail={detail} />
      <div className="grid2">
        <RepertoireCard code={detail.data.technique.code} name={detail.data.technique.name} />
        <CounterCard code={detail.data.technique.code} name={detail.data.technique.name} />
      </div>
      <ScoresCard code={detail.data.technique.code} />
    </>
  );
}

function HoldDownNotice() {
  const { glossary } = useMetaData();
  const entry = glossary.find((item) => item.term === "Hold-down scores");
  return entry ? <Notice>{entry.definition}</Notice> : null;
}

function ChangeTechnique({ code }: { code: string }) {
  const selectId = useId();
  const { techniques } = useMetaData();
  const navigate = useNavigate();
  const search = useFilterSearch();
  return (
    <div className="change-technique">
      <label htmlFor={selectId} className="field-label">
        Change technique
      </label>
      <select
        id={selectId}
        className="trend-select"
        value={code}
        onChange={(event) => void navigate({ pathname: `/techniques/${event.target.value}`, search })}
      >
        {techniques.map((technique) => (
          <option key={technique.code} value={technique.code}>
            {technique.name}
          </option>
        ))}
      </select>
    </div>
  );
}
