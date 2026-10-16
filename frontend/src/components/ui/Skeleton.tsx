import styles from "./Skeleton.module.css";

export function Skeleton({ blocks = 3 }: { blocks?: number }) {
  return (
    <div className={styles.skeleton} role="status">
      <span className="sr">Loading…</span>
      {Array.from({ length: blocks }, (_, index) => (
        <div key={index} className={styles.block} aria-hidden="true" />
      ))}
    </div>
  );
}
