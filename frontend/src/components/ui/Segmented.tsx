import { InfoTip } from "./InfoTip";
import styles from "./Segmented.module.css";

type Option = { value: string; label: string };
type SegmentedProps = {
  legend: string;
  term?: string;
  options: readonly Option[];
  value: string;
  onChange: (value: string) => void;
};

export function Segmented({ legend, term, options, value, onChange }: SegmentedProps) {
  return (
    <fieldset>
      <legend>
        {legend}
        {term && <InfoTip term={term} />}
      </legend>
      <div className={styles.segments}>
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            aria-pressed={option.value === value}
            onClick={() => onChange(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </fieldset>
  );
}
