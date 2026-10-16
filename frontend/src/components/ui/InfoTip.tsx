import { useMetaData } from "../../app/meta";
import styles from "./InfoTip.module.css";

export function InfoTip({ term }: { term: string }) {
  const { glossary } = useMetaData();
  const entry = glossary.find((item) => item.term === term);
  if (!entry) return null;
  return (
    <button type="button" className={styles.info} aria-label={`About ${term}`} data-tip={`${term}\n${entry.definition}`}>
      i
    </button>
  );
}
