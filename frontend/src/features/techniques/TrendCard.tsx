import { useId } from "react";
import { useTechnique } from "../../api/hooks";
import { LineChart } from "../../components/charts/LineChart";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { Loaded } from "../../components/ui/Loaded";
import { Skeleton } from "../../components/ui/Skeleton";
import { useFilters } from "../../filters/useFilters";
import { useTierList } from "./useTierList";

const DESCRIPTION =
  "Each year's share of the scores for one technique of the tier list: is it rising or falling? Dashed lines mark a ruleset change; with fewer than 3 years there is no trend to read.";

export function TrendCard() {
  const selectId = useId();
  const { filters, params, setPageParams } = useFilters();
  const { query: tier } = useTierList();
  const options = (tier.data?.data.rows ?? []).flatMap((row) => (row.technique ? [row.technique] : []));
  const chosen = params.get("trend");
  // A technique that left the tier list (another filter, another sort) gives way to the first row.
  const code = options.find((technique) => technique.code === chosen)?.code ?? options.at(0)?.code;
  const detail = useTechnique(code, filters);
  // A failing tier list already shows its error and Retry in the card above.
  if (tier.isError) return null;
  if (tier.data === undefined) return <Skeleton blocks={1} />;
  if (code === undefined) {
    return (
      <Card title="Trend" description={DESCRIPTION}>
        <EmptyState>No technique in the tier list for these filters.</EmptyState>
      </Card>
    );
  }
  return (
    <Loaded query={detail}>
      {(technique) => (
        <Card
          title="Trend"
          sample={technique.data.trend.sample}
          right={
            <>
              <label htmlFor={selectId} className="sr">
                Technique of the trend
              </label>
              <select
                id={selectId}
                className="trend-select"
                value={code}
                onChange={(event) => setPageParams({ trend: event.target.value })}
              >
                {options.map((option) => (
                  <option key={option.code} value={option.code}>
                    {option.name}
                  </option>
                ))}
              </select>
            </>
          }
          description={DESCRIPTION}
        >
          {technique.data.trend.points.length ? (
            <LineChart
              points={technique.data.trend.points}
              rulesetChanges={technique.data.trend.ruleset_changes}
              label={`Share of the scores with ${technique.data.technique.name} per year`}
            />
          ) : (
            <EmptyState>No score with this technique in these years.</EmptyState>
          )}
        </Card>
      )}
    </Loaded>
  );
}
