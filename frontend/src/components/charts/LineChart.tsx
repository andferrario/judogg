import type { TrendPoint } from "../../api/types";
import { formatPercent } from "../../format/format";
import styles from "./LineChart.module.css";

const WIDTH = 640;
const HEIGHT = 240;
const LEFT = 46;
const RIGHT = 20;
const TOP = 22;
const BOTTOM = 30;
const INNER_WIDTH = WIDTH - LEFT - RIGHT;
const INNER_HEIGHT = HEIGHT - TOP - BOTTOM;
const GRID_LINES = 4;

export function niceMax(value: number): number {
  if (value <= 0) return 1;
  const magnitude = 10 ** Math.floor(Math.log10(value));
  const step = [1, 2, 2.5, 5, 10].find((candidate) => value / magnitude <= candidate) ?? 10;
  return step * magnitude;
}

type LineChartProps = { points: readonly TrendPoint[]; rulesetChanges: readonly number[]; label: string };

export function LineChart({ points, rulesetChanges, label }: LineChartProps) {
  const max = niceMax(Math.max(0.01, ...points.map((point) => point.share ?? 0)));
  const x = (index: number) => LEFT + (points.length === 1 ? INNER_WIDTH / 2 : (index * INNER_WIDTH) / (points.length - 1));
  const y = (share: number | null) => TOP + INNER_HEIGHT - ((share ?? 0) / max) * INNER_HEIGHT;
  const step = points.length > 1 ? INNER_WIDTH / (points.length - 1) : INNER_WIDTH;
  const line = points.map((point, index) => `${index ? "L" : "M"}${x(index).toFixed(1)},${y(point.share).toFixed(1)}`).join("");
  const describe = (point: TrendPoint) => `${point.year}: ${formatPercent(point.share, 1)} (${point.n} of ${point.total})`;
  const gridDecimals = max < 0.05 ? 1 : 0;

  return (
    <figure className={styles.figure}>
      <svg className={styles.chart} viewBox={`0 0 ${WIDTH} ${HEIGHT}`} width="100%" role="img" aria-label={label}>
        {Array.from({ length: GRID_LINES + 1 }, (_, line) => {
          const value = (max * line) / GRID_LINES;
          return (
            <g key={line}>
              <line className={line ? styles.grid : styles.base} x1={LEFT} x2={WIDTH - RIGHT} y1={y(value)} y2={y(value)} />
              <text data-grid-label x={LEFT - 8} y={y(value) + 4} textAnchor="end">
                {(value * 100).toFixed(gridDecimals)}%
              </text>
            </g>
          );
        })}
        {points.map((point, index) => {
          if (index === 0 || !rulesetChanges.includes(point.year)) return null;
          const between = (x(index - 1) + x(index)) / 2;
          return (
            <g key={`change-${point.year}`}>
              <line data-ruleset-change className={styles.change} x1={between} x2={between} y1={TOP - 6} y2={TOP + INNER_HEIGHT} />
              <text x={between + 4} y={TOP}>
                {point.year}
              </text>
            </g>
          );
        })}
        {points.length > 1 && (
          <>
            <path className={styles.area} d={`${line}L${x(points.length - 1)},${TOP + INNER_HEIGHT}L${x(0)},${TOP + INNER_HEIGHT}Z`} />
            <path className={styles.line} d={line} />
          </>
        )}
        {points.map((point, index) => (
          <g key={point.year}>
            <circle className={styles.point} cx={x(index)} cy={y(point.share)} r={4} />
            <text x={x(index)} y={HEIGHT - 10} textAnchor="middle">
              {point.year}
            </text>
            <rect className={styles.hit} x={x(index) - step / 2} y={TOP} width={step} height={INNER_HEIGHT} data-tip={describe(point)} />
          </g>
        ))}
      </svg>
      <ul className="sr" aria-label={`${label}: values`}>
        {points.map((point) => (
          <li key={point.year}>{describe(point)}</li>
        ))}
      </ul>
    </figure>
  );
}
