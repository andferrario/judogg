import { useOverview } from "../../api/hooks";
import { PageFrame } from "../../app/PageFrame";
import { useFilters } from "../../filters/useFilters";
import { OutcomesCard } from "./OutcomesCard";
import { OverviewKpis } from "./OverviewKpis";
import { TierCard } from "./TierCard";
import { TimingCard } from "./TimingCard";
import { TrendCard } from "./TrendCard";
import { WeightMatrixCard } from "./WeightMatrixCard";

export function TechniquesPage() {
  const { filters } = useFilters();
  const overview = useOverview(filters);
  return (
    <PageFrame title="Techniques" query={overview}>
      {(data) => (
        <>
          <OverviewKpis overview={data} />
          <TierCard />
          <div className="grid2">
            <TimingCard overview={data} />
            <TrendCard />
          </div>
          <WeightMatrixCard />
          <OutcomesCard />
        </>
      )}
    </PageFrame>
  );
}
