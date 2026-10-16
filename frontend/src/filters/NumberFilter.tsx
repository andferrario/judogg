import { useId, useState } from "react";
import styles from "./FilterRail.module.css";

type NumberFilterProps = { label: string; value: string; min: number; max: number; onCommit: (value: string) => void };

export function NumberFilter({ label, value, min, max, onCommit }: NumberFilterProps) {
  const id = useId();
  const [draft, setDraft] = useState(value);
  const [shown, setShown] = useState(value);
  // A new value from the URL (a reset, the Back button) replaces the draft.
  if (value !== shown) {
    setShown(value);
    setDraft(value);
  }
  // Committed on Enter or blur, not on every keystroke: typing "15" must not request "1" first.
  const commit = () => {
    const number = Number(draft);
    if (draft !== "" && Number.isInteger(number) && number >= min && number <= max) {
      if (String(number) !== value) onCommit(String(number));
    } else {
      setDraft(value);
    }
  };
  return (
    <div className={styles.inline}>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        type="number"
        inputMode="numeric"
        min={min}
        max={max}
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        onBlur={commit}
        onKeyDown={(event) => {
          if (event.key === "Enter") commit();
        }}
      />
    </div>
  );
}
