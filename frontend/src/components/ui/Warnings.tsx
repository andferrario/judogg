import type { WarningItem } from "../../api/types";
import styles from "./Warnings.module.css";

export function Warnings({ warnings }: { warnings: readonly WarningItem[] }) {
  return (
    <div className={styles.list} role="status">
      {warnings.map((warning) => (
        <p key={warning.code} className={styles.warning}>
          <strong>Heads-up.</strong> {warning.message}
        </p>
      ))}
    </div>
  );
}
