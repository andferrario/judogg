import { usePenalties } from "../../api/hooks";
import { PageFrame } from "../../app/PageFrame";
import { useFilters } from "../../filters/useFilters";
import {
  GroupsCard,
  PenaltyKpis,
  PenaltyTimingCard,
  PenaltyWeightsCard,
  ReasonsCard,
  ShidoNumberCard,
} from "./PenaltyCards";

export function PenaltiesPage() {
  const { filters } = useFilters();
  const penalties = usePenalties(filters);
  return (
    <PageFrame title="Penalties" query={penalties}>
      {(response) => (
        <>
          <PenaltyKpis response={response} />
          <ReasonsCard response={response} />
          <div className="grid2">
            <GroupsCard response={response} />
            <PenaltyTimingCard response={response} />
          </div>
          <div className="grid2">
            <PenaltyWeightsCard response={response} />
            <ShidoNumberCard response={response} />
          </div>
        </>
      )}
    </PageFrame>
  );
}
