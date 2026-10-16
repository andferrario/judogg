import { useId, useState, type KeyboardEvent } from "react";
import { useLocation, useNavigate } from "react-router";
import { useAthleteSearch } from "../api/hooks";
import { useMetaData } from "../app/meta";
import { filterSearch } from "../filters/filters";
import { athleteOptions, catalogueOptions, type SearchOption } from "./searchOptions";
import styles from "./Search.module.css";
import { useDebouncedValue } from "./useDebouncedValue";

const MIN_ATHLETE_TEXT = 2;
const DEBOUNCE_MS = 200;

export function Search() {
  const meta = useMetaData();
  const navigate = useNavigate();
  const { search } = useLocation();
  const inputId = useId();
  const listId = useId();
  const [text, setText] = useState("");
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const trimmed = text.trim();
  const athletes = useAthleteSearch(useDebouncedValue(trimmed, DEBOUNCE_MS));

  const options = [
    ...(trimmed.length >= MIN_ATHLETE_TEXT ? athleteOptions(athletes.data?.rows ?? []) : []),
    ...catalogueOptions(meta, text),
  ];
  const expanded = open && options.length > 0;
  const current = Math.min(active, options.length - 1);
  const optionId = (index: number) => `${listId}-${index}`;

  const choose = (option: SearchOption) => {
    void navigate({ pathname: option.pathname, search: filterSearch(new URLSearchParams(search), option.extra) });
    setText("");
    setOpen(false);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if ((event.key === "ArrowDown" || event.key === "ArrowUp") && options.length > 0) {
      event.preventDefault();
      const step = event.key === "ArrowDown" ? 1 : -1;
      setOpen(true);
      setActive((current + step + options.length) % options.length);
    } else if (event.key === "Enter" && expanded) {
      event.preventDefault();
      choose(options[current]);
    } else if (event.key === "Escape") {
      setOpen(false);
    }
  };

  return (
    <div className={styles.search}>
      <label htmlFor={inputId} className="sr">
        Search a technique, a shido reason or a judoka
      </label>
      <input
        id={inputId}
        className={styles.input}
        type="search"
        role="combobox"
        aria-expanded={expanded}
        aria-controls={listId}
        aria-autocomplete="list"
        aria-activedescendant={expanded ? optionId(current) : undefined}
        placeholder="Search technique, shido reason or judoka"
        autoComplete="off"
        value={text}
        onChange={(event) => {
          setText(event.target.value);
          setActive(0);
          setOpen(true);
        }}
        onKeyDown={onKeyDown}
        onBlur={() => setOpen(false)}
      />
      <ul id={listId} role="listbox" aria-label="Suggestions" className={styles.list} hidden={!expanded}>
        {expanded &&
          options.map((option, index) => (
            <li
              key={option.id}
              id={optionId(index)}
              role="option"
              tabIndex={-1}
              aria-selected={index === current}
              className={styles.option}
              onMouseDown={(event) => {
                // Keeps the focus in the input, so that its blur does not close the list before the choice.
                event.preventDefault();
                choose(option);
              }}
            >
              <span>{option.label}</span> <span className={styles.detail}>{option.detail}</span>
            </li>
          ))}
      </ul>
    </div>
  );
}
