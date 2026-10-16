import type { SideCounts, ValueCounts } from "../../api/types";
import { formatPercent } from "../../format/format";
import styles from "./Bars.module.css";

// Tooltips show on hover only: their text is also in the page for keyboards, touch screens and screen readers.

const VALUES = ["ippon", "waza_ari", "yuko"] as const;

export const VALUE_CLASS = { ippon: styles.ippon, waza_ari: styles.waza, yuko: styles.yuko };

export function widthOf(fraction: number): string {
  return `${Math.max(0, Math.min(1, fraction)) * 100}%`;
}

type StackedBarProps = { counts: ValueCounts; fraction: number; tip?: string };

export function StackedBar({ counts, fraction, tip }: StackedBarProps) {
  return (
    <div className={styles.stacked} style={{ width: widthOf(fraction) }} data-tip={tip}>
      {VALUES.filter((value) => counts[value] > 0).map((value) => (
        <i key={value} className={VALUE_CLASS[value]} style={{ flexGrow: counts[value] }} />
      ))}
      {tip && <span className="sr">{tip}</span>}
    </div>
  );
}

type HBarProps = { fraction: number; tip?: string; dimmed?: boolean; tone?: "score" | "penalty" };

export function HBar({ fraction, tip, dimmed = false, tone = "score" }: HBarProps) {
  return (
    <div
      className={styles.hbar}
      style={{ width: widthOf(fraction) }}
      data-tip={tip}
      data-dimmed={dimmed || undefined}
      data-tone={tone}
    >
      {tip && <span className="sr">{tip}</span>}
    </div>
  );
}

export function MiniSide({ side }: { side: SideCounts }) {
  const text = `Left ${side.left} · Right ${side.right} · Unknown ${side.unknown}`;
  return (
    <div className={styles.mini} role="img" aria-label={text} data-tip={text}>
      {side.left > 0 && <i className={styles.left} style={{ flexGrow: side.left }} />}
      {side.right > 0 && <i className={styles.right} style={{ flexGrow: side.right }} />}
      {side.unknown > 0 && <i className={styles.unknown} style={{ flexGrow: side.unknown }} />}
    </div>
  );
}

export function SideBar({ side }: { side: SideCounts }) {
  const known = side.left + side.right;
  if (known === 0) {
    return (
      <div className={styles.side}>
        <span className={styles.value}>–</span>
        <div className={styles.track}>
          <div />
          <div />
        </div>
        <span className={styles.value}>–</span>
      </div>
    );
  }
  const left = side.left / known;
  const right = side.right / known;
  const unknown = side.unknown / (known + side.unknown);
  const tip = `Left ${side.left} · Right ${side.right} · Unknown ${side.unknown} (${formatPercent(unknown)})`;
  return (
    <div className={styles.side} data-tip={tip}>
      <span className="sr">{tip}</span>
      <span className={styles.value}>{formatPercent(left)}</span>
      <div className={styles.track}>
        <div>
          <i style={{ width: widthOf(left) }} />
        </div>
        <div>
          <i style={{ width: widthOf(right) }} />
        </div>
      </div>
      <span className={styles.value}>{formatPercent(right)}</span>
    </div>
  );
}

export function ScoreLegend() {
  return (
    <div className={styles.legend}>
      <span>
        <i className={styles.ippon} />
        Ippon
      </span>
      <span>
        <i className={styles.waza} />
        Waza-ari
      </span>
      <span>
        <i className={styles.yuko} />
        Yuko
      </span>
    </div>
  );
}

export function SideLegend() {
  return (
    <div className={styles.legend}>
      <span>
        <i className={styles.left} />
        Left
      </span>
      <span>
        <i className={styles.right} />
        Right
      </span>
      <span>
        <i className={styles.unknown} />
        Unknown
      </span>
    </div>
  );
}

type SplitPart = { key: string; label: string; n: number; share: number | null };

const SPLIT_CLASSES = [styles.ippon, styles.waza, styles.yuko, styles.unknown, styles.left];

export function SplitBar({ parts }: { parts: readonly SplitPart[] }) {
  const classOf = (index: number) => SPLIT_CLASSES[index % SPLIT_CLASSES.length];
  return (
    <>
      <div className={styles.split}>
        {parts.map((part, index) => (
          <div
            key={part.key}
            data-part
            className={classOf(index)}
            style={{ flexGrow: part.n }}
            data-tip={`${part.label}: ${part.n} (${formatPercent(part.share, 1)})`}
          >
            <span className="sr">{`${part.label}: ${part.n} (${formatPercent(part.share, 1)})`}</span>
          </div>
        ))}
      </div>
      <div className={`${styles.legend} ${styles.splitLegend}`}>
        {parts.map((part, index) => (
          <span key={part.key}>
            <i className={classOf(index)} />
            {part.label} {formatPercent(part.share)}
          </span>
        ))}
      </div>
    </>
  );
}
