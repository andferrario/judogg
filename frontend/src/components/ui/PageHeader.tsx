import type { ReactNode } from "react";
import styles from "./PageHeader.module.css";

type PageHeaderProps = {
  title: ReactNode;
  summary?: ReactNode;
  note?: ReactNode;
  big?: boolean;
  back?: ReactNode;
  children?: ReactNode;
};

export function PageHeader({ title, summary, note, big = false, back, children }: PageHeaderProps) {
  return (
    <header className={styles.head}>
      <div>
        {back && <p className={styles.back}>{back}</p>}
        <h1 className={big ? styles.big : undefined} data-big={big || undefined}>
          {title}
        </h1>
        {summary && <p className={styles.summary}>{summary}</p>}
        {note && <p className={styles.note}>{note}</p>}
      </div>
      {children}
    </header>
  );
}
