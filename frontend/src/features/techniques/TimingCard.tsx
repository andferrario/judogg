import type { OverviewResponse } from "../../api/types";
import { ScoreLegend } from "../../components/charts/Bars";
import { ColumnChart } from "../../components/charts/ColumnChart";
import { Card } from "../../components/ui/Card";

export function TimingCard({ overview }: { overview: OverviewResponse }) {
  return (
    <Card
      title="When scores happen"
      sample={overview.data.sample}
      right={<ScoreLegend />}
      description="Scores per 30-second block of regulation time, golden score apart: when in the contest do techniques score? Counts, not rates: more contests reach 3:00 than golden score."
    >
      <ColumnChart bins={overview.data.timing} label="Scores per 30-second block" />
    </Card>
  );
}
