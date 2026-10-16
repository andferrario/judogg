import type { PenaltyBin, TimingBin } from "../../api/types";
import { VALUE_CLASS } from "./Bars";
import styles from "./ColumnChart.module.css";

const VALUES = ["ippon", "waza_ari", "yuko"] as const;
const GOLDEN_SCORE_BIN = 8;
// Headroom above the tallest column for its value label.
const TALLEST = 85;

type Bin = TimingBin | PenaltyBin;

function isScoreBin(bin: Bin): bin is TimingBin {
  return "ippon" in bin;
}

function describe(bin: Bin): string {
  return isScoreBin(bin)
    ? `${bin.label}: ${bin.n} scores (Ippon ${bin.ippon}, Waza-ari ${bin.waza_ari}, Yuko ${bin.yuko})`
    : `${bin.label}: ${bin.n} penalties`;
}

type ColumnChartProps = { bins: readonly Bin[]; label: string };

export function ColumnChart({ bins, label }: ColumnChartProps) {
  const max = Math.max(1, ...bins.map((bin) => bin.n));
  return (
    <figure className={styles.figure}>
      <div className={styles.columns} role="img" aria-label={label}>
        {bins.map((bin) => (
          <div
            key={bin.bin}
            className={styles.column}
            data-gs={bin.bin === GOLDEN_SCORE_BIN || undefined}
            data-tip={describe(bin).replace(": ", "\n")}
          >
            <span className={styles.value}>{bin.n}</span>
            <div className={styles.stack} data-stack style={{ height: `${(bin.n / max) * TALLEST}%` }}>
              {isScoreBin(bin)
                ? VALUES.filter((value) => bin[value] > 0).map((value) => (
                    <i key={value} className={VALUE_CLASS[value]} style={{ flexGrow: bin[value] }} />
                  ))
                : bin.n > 0 && <i className={styles.penalty} style={{ flexGrow: 1 }} />}
            </div>
          </div>
        ))}
      </div>
      <div className={styles.axis} data-axis aria-hidden="true">
        {bins.map((bin) => (
          <span key={bin.bin} data-gs={bin.bin === GOLDEN_SCORE_BIN || undefined}>
            {bin.bin === GOLDEN_SCORE_BIN ? "GS" : bin.label.split("–")[0]}
          </span>
        ))}
      </div>
      <ul className="sr" aria-label={`${label}: values`}>
        {bins.map((bin) => (
          <li key={bin.bin}>{describe(bin)}</li>
        ))}
      </ul>
    </figure>
  );
}
