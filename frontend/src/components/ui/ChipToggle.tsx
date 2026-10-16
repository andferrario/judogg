import type { ReactNode } from "react";
import styles from "./ChipToggle.module.css";

type ChipToggleProps = {
  pressed: boolean;
  onClick: () => void;
  tip?: string;
  /** Selectable, but there is nothing behind it (a ruleset without contests). */
  dimmed?: boolean;
  /** A word rather than a code: body font instead of mono. */
  text?: boolean;
  /** Pressed and not switchable off: the click does nothing, the tip says why. */
  locked?: boolean;
  children: ReactNode;
};

export function ChipToggle({ pressed, onClick, tip, dimmed, text, locked = false, children }: ChipToggleProps) {
  return (
    <button
      type="button"
      className={styles.chip}
      aria-pressed={pressed}
      aria-disabled={locked || undefined}
      data-tip={tip}
      data-dimmed={dimmed || undefined}
      data-text={text || undefined}
      onClick={locked ? undefined : onClick}
    >
      {children}
    </button>
  );
}
