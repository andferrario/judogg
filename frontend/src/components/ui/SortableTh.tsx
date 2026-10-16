import styles from "./SortableTh.module.css";

type SortableThProps = {
  label: string;
  column: string;
  sort: string;
  order: "asc" | "desc";
  onSort: (column: string) => void;
  numeric?: boolean;
};

export function SortableTh({ label, column, sort, order, onSort, numeric = false }: SortableThProps) {
  const active = column === sort;
  return (
    <th
      scope="col"
      className={numeric ? "r" : undefined}
      aria-sort={active ? (order === "asc" ? "ascending" : "descending") : undefined}
    >
      <button type="button" className={styles.sort} data-active={active || undefined} onClick={() => onSort(column)}>
        {label}
        {active && <span aria-hidden="true">{order === "asc" ? " ↑" : " ↓"}</span>}
      </button>
    </th>
  );
}
