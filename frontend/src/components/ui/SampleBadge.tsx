import type { Sample } from "../../api/types";
import styles from "./SampleBadge.module.css";

export function SampleBadge({ sample }: { sample?: Sample }) {
  if (!sample || sample.status === "ok") return null;
  const small = sample.status === "small";
  const tip = small
    ? `Small sample: ${sample.n} ${sample.unit}. Read with care.`
    : `Insufficient sample: ${sample.n} ${sample.unit}. Not meaningful.`;
  return (
    <span className={styles.badge} data-status={sample.status} data-tip={tip}>
      {small ? "small sample" : "insufficient"} · n={sample.n}
    </span>
  );
}
