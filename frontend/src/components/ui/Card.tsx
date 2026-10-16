import { useId, type ReactNode } from "react";
import type { Sample } from "../../api/types";
import styles from "./Card.module.css";
import { InfoTip } from "./InfoTip";
import { SampleBadge } from "./SampleBadge";

type CardProps = {
  title: string;
  /** What the card shows, which question it answers and how to read it, limits included. */
  description: ReactNode;
  term?: string;
  right?: ReactNode;
  sample?: Sample;
  id?: string;
  children: ReactNode;
};

export function Card({ title, description, term, right, sample, id, children }: CardProps) {
  const titleId = useId();
  return (
    <section className={styles.card} id={id} aria-labelledby={titleId} data-sample={sample?.status}>
      <div className={styles.head}>
        <div className={styles.title}>
          <h2 id={titleId}>{title}</h2>
          {term && <InfoTip term={term} />}
        </div>
        <div className={styles.right}>
          {right}
          <SampleBadge sample={sample} />
        </div>
      </div>
      <p className={styles.description}>{description}</p>
      <div className={styles.body}>{children}</div>
    </section>
  );
}
