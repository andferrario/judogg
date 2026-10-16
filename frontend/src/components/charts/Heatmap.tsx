import { Fragment } from "react";
import { Link, type To } from "react-router";
import styles from "./Heatmap.module.css";

export type Fill = { background: string; lightText: boolean };
export type HeatCell = { key: string; text: string; fill: Fill; tip: string; label: string; to: To };
export type HeatRow = { key: string; label: string; dimmed: boolean; cells: (HeatCell | null)[] };
type HeatmapProps = {
  columns: readonly { key: string; label: string }[];
  rows: readonly HeatRow[];
  rowHeadWidth?: number;
  replace?: boolean;
};

// Above this intensity of the strongest colour, dark text would not read.
const LIGHT_TEXT_FROM = 0.55;

export const NEUTRAL_FILL: Fill = { background: "var(--surface-2)", lightText: false };

function clamp(value: number, low: number, high: number): number {
  return Math.max(low, Math.min(high, value));
}

export function sequentialFill(fraction: number): Fill {
  const share = clamp(fraction, 0, 1);
  return {
    background: `color-mix(in oklab, var(--seq-hi) ${Math.round(share * 100)}%, var(--seq-lo))`,
    lightText: share > LIGHT_TEXT_FROM,
  };
}

// A lift of 2 and one of 0.5 are as far from 1: the scale is logarithmic, capped at twice and at half.
export function divergingFill(lift: number | null): Fill {
  const value = lift ?? 1;
  const distance = value > 0 ? clamp(Math.log2(value), -1, 1) : -1;
  const end = distance >= 0 ? "var(--div-pos)" : "var(--div-neg)";
  return {
    background: `color-mix(in oklab, ${end} ${Math.round(Math.abs(distance) * 100)}%, var(--div-mid))`,
    lightText: Math.abs(distance) > LIGHT_TEXT_FROM,
  };
}

export function Heatmap({ columns, rows, rowHeadWidth = 72, replace = false }: HeatmapProps) {
  return (
    <div className="tw">
      <div
        className={styles.heat}
        style={{ gridTemplateColumns: `${rowHeadWidth}px repeat(${columns.length}, minmax(0, 1fr))` }}
      >
        <span />
        {columns.map((column) => (
          <span key={column.key} className={styles.columnHead}>
            {column.label}
          </span>
        ))}
        {rows.map((row) => (
          <Fragment key={row.key}>
            <span className={styles.rowHead}>{row.label}</span>
            {row.cells.map((cell, index) =>
              cell === null ? (
                <span key={`empty-${index}`} className={styles.empty} data-empty />
              ) : (
                <Link
                  key={cell.key}
                  className={styles.cell}
                  to={cell.to}
                  replace={replace}
                  aria-label={cell.label}
                  data-tip={cell.tip}
                  data-heat-cell
                  data-dimmed={row.dimmed || undefined}
                  style={{ background: cell.fill.background, color: cell.fill.lightText ? "var(--on-hi)" : "var(--fg)" }}
                >
                  {cell.text}
                </Link>
              ),
            )}
          </Fragment>
        ))}
      </div>
    </div>
  );
}

export function DivergingLegend() {
  return (
    <div className={styles.legend}>
      <span>
        <i style={{ background: "var(--div-neg)" }} />
        below 1
      </span>
      <span>
        <i style={{ background: "var(--div-mid)" }} />1
      </span>
      <span>
        <i style={{ background: "var(--div-pos)" }} />
        above 1
      </span>
    </div>
  );
}
