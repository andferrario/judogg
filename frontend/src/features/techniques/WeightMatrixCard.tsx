import { useLocation } from "react-router";
import { useWeightMatrix } from "../../api/hooks";
import { Heatmap, sequentialFill, type HeatRow } from "../../components/charts/Heatmap";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { Loaded } from "../../components/ui/Loaded";
import { filterSearch } from "../../filters/filters";
import { useFilters } from "../../filters/useFilters";
import { formatPercent, weightLabel } from "../../format/format";

export function WeightMatrixCard() {
  const { filters } = useFilters();
  const params = new URLSearchParams(useLocation().search);
  const matrix = useWeightMatrix(filters);
  return (
    <Loaded query={matrix}>
      {(response) => {
        const { techniques, rows } = response.data;
        const unit = response.filters.count_by === "athlete" ? "athletes" : "scores";
        const names = new Map(techniques.map((technique) => [technique.code, technique.name]));
        const max = Math.max(0.01, ...rows.flatMap((row) => row.cells.map((cell) => cell.share ?? 0)));
        const heatRows: HeatRow[] = rows.map((row) => ({
          key: row.weight.code,
          label: weightLabel(row.weight),
          dimmed: row.sample.status === "insufficient",
          cells: row.cells.map((cell) => {
            const where = `${weightLabel(row.weight)} · ${names.get(cell.technique) ?? cell.technique}`;
            const value = `${formatPercent(cell.share, 1)} (${cell.n} of ${row.total} ${unit})`;
            return {
              key: cell.technique,
              text: formatPercent(cell.share),
              fill: sequentialFill((cell.share ?? 0) / max),
              tip: `${where}\n${value}`,
              label: `${where}: ${value}`,
              to: {
                pathname: `/techniques/${cell.technique}`,
                search: filterSearch(params, { weight: row.weight.code, gender: row.weight.gender }),
              },
            };
          }),
        }));
        return (
          <Card
            title="Weight × technique"
            description={`Each technique's share of the ${unit} of each weight: which techniques work in which categories? The columns are the techniques that score most overall; a cell opens the technique on that weight.`}
          >
            {techniques.length === 0 || rows.length === 0 ? (
              <EmptyState>No score with these filters. Widen the filters.</EmptyState>
            ) : (
              <Heatmap columns={techniques.map((technique) => ({ key: technique.code, label: technique.name }))} rows={heatRows} />
            )}
          </Card>
        );
      }}
    </Loaded>
  );
}
