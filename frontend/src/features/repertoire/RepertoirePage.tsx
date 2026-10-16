import { useId } from "react";
import { useRepertoire, useRepertoirePairs } from "../../api/hooks";
import { useMetaData } from "../../app/meta";
import { PageFrame } from "../../app/PageFrame";
import { useFilters } from "../../filters/useFilters";
import { FrequentPairsCard, LiftMatrixCard } from "./PairsCards";
import { CompanionsCard, PairAthletesCard, RepertoireIntro, RepertoireKpis } from "./RepertoireCards";

export function RepertoirePage() {
  const meta = useMetaData();
  const { filters, params } = useFilters();
  const pairs = useRepertoirePairs(filters);
  // The default technique is the first of the lift matrix of these filters: wait for it (not for the old
  // filters' matrix, kept on screen meanwhile) rather than load another technique first.
  const fallback =
    pairs.data && !pairs.isPlaceholderData
    ? (pairs.data.data.matrix.techniques.at(0)?.code ?? meta.techniques.at(0)?.code)
    : pairs.isError
      ? meta.techniques.at(0)?.code
      : undefined;
  const code = params.get("technique") ?? fallback;
  const repertoire = useRepertoire(code, filters, params.get("with") ?? undefined);
  return (
    <PageFrame title="Repertoire" query={repertoire} aside={<TechniqueSelect code={code ?? repertoire.data?.data.technique.code} />}>
      {(response) => (
        <>
          <RepertoireIntro response={response} />
          <RepertoireKpis response={response} />
          <div className="grid2">
            <CompanionsCard response={response} />
            <PairAthletesCard response={response} />
          </div>
          <FrequentPairsCard query={pairs} />
          <LiftMatrixCard query={pairs} />
        </>
      )}
    </PageFrame>
  );
}

function TechniqueSelect({ code }: { code: string | undefined }) {
  const selectId = useId();
  const { techniques } = useMetaData();
  const { setPageParams } = useFilters();
  return (
    <div className="change-technique">
      <label htmlFor={selectId} className="field-label">
        Technique
      </label>
      <select
        id={selectId}
        className="trend-select"
        value={code ?? ""}
        // The companion belongs to the old technique (and the API refuses a technique paired with itself).
        onChange={(event) => setPageParams({ technique: event.target.value, with: null })}
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
