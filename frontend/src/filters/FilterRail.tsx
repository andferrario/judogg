import { useId, useState } from "react";
import { useMatch } from "react-router";
import { useMetaData } from "../app/meta";
import { ChipToggle } from "../components/ui/ChipToggle";
import { InfoTip } from "../components/ui/InfoTip";
import { Segmented } from "../components/ui/Segmented";
import { DataStrip } from "./DataStrip";
import styles from "./FilterRail.module.css";
import {
  countChanged,
  genderChange,
  listParam,
  rulesetToggle,
  selectedRulesets,
  sideChange,
  toggleValue,
  yearChange,
  yearRange,
} from "./filters";
import { NumberFilter } from "./NumberFilter";
import { useFilters } from "./useFilters";

const PHONE = "(max-width: 900px)";
const DOMAINS = [
  { value: "", label: "All" },
  { value: "standing", label: "Standing" },
  { value: "ground", label: "Ground" },
];
const SIDES = [
  { value: "left", label: "Left" },
  { value: "right", label: "Right" },
  { value: "unknown", label: "Unknown" },
];
const COUNT_BY = [
  { value: "event", label: "Event" },
  { value: "athlete", label: "Athlete" },
];

function isPhone(): boolean {
  return typeof window.matchMedia === "function" && window.matchMedia(PHONE).matches;
}

export function FilterRail() {
  const onCoverage = useMatch("/coverage") !== null;
  const onAthlete = useMatch("/athletes/:id") !== null;
  const { params } = useFilters();
  // On a phone the filters start collapsed, so that the page content comes first.
  const [open] = useState(() => !isPhone());
  const changed = countChanged(params);
  return (
    <>
      {!onCoverage && !onAthlete && <DataStrip />}
      <details className={styles.details} open={open}>
        <summary className={styles.summary}>
          Filters <span className={styles.count}>{changed ? `${changed} changed` : ""}</span>
        </summary>
        {onCoverage && <p className={styles.note}>Coverage is not filtered.</p>}
        {onAthlete && (
          <p className={styles.note}>
            The judoka page is not filtered: it shows the athlete's whole career. Your filters are kept for the other
            pages.
          </p>
        )}
        {!onCoverage && !onAthlete && <FilterControls />}
      </details>
    </>
  );
}

function FilterControls() {
  const meta = useMetaData();
  const { params, change, reset } = useFilters();
  const fromId = useId();
  const toId = useId();
  const countryId = useId();
  const gender = params.get("gender") ?? meta.defaults.gender;
  const weights = meta.weights.filter((weight) => gender === "all" || weight.gender === gender);
  const selectedWeights = listParam(params, "weight");
  const rulesets = selectedRulesets(params, meta.defaults);
  const years = yearRange(params, meta);
  const sides = listParam(params, "side");
  const genders = [{ value: "all", label: "All" }, ...meta.genders.map((g) => ({ value: g.code, label: g.label }))];

  return (
    <div className={styles.controls}>
      <Segmented
        legend="Gender"
        options={genders}
        value={gender}
        onChange={(value) => change(genderChange(params, value, meta.weights))}
      />

      <fieldset>
        <legend>Weight</legend>
        <div className={styles.chips}>
          <ChipToggle text pressed={selectedWeights.length === 0} onClick={() => change({ weight: null })}>
            All
          </ChipToggle>
          {weights.map((weight) => (
            <ChipToggle
              key={weight.code}
              pressed={selectedWeights.includes(weight.code)}
              tip={`${weight.contests} contests loaded`}
              onClick={() => change({ weight: toggleValue(selectedWeights, weight.code).join(",") })}
            >
              {weight.label}
              {gender === "all" && (weight.gender === "m" ? "M" : "W")}
            </ChipToggle>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend>
          Ruleset
          <InfoTip term="Ruleset" />
        </legend>
        <div className={styles.chips}>
          {meta.rulesets.map((ruleset) => (
            <ChipToggle
              key={ruleset.id}
              pressed={rulesets.includes(String(ruleset.id))}
              dimmed={ruleset.contests === 0}
              tip={`yuko: ${ruleset.has_yuko ? "yes" : "no"} · koka: ${ruleset.has_koka ? "yes" : "no"} · max shido ${ruleset.max_shido} · ${ruleset.contests} contests loaded`}
              onClick={() => change(rulesetToggle(params, String(ruleset.id), meta.defaults))}
            >
              {ruleset.label}
            </ChipToggle>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend>Years</legend>
        <div className={styles.two}>
          <div className={styles.field}>
            <label htmlFor={fromId}>From</label>
            <select
              id={fromId}
              className={styles.select}
              value={years.from ?? ""}
              disabled={years.years.length === 0}
              onChange={(event) => change(yearChange(years, "year_from", event.target.value))}
            >
              {years.years
                .filter((year) => years.to === undefined || year <= years.to)
                .map((year) => (
                  <option key={year}>{year}</option>
                ))}
            </select>
          </div>
          <div className={styles.field}>
            <label htmlFor={toId}>To</label>
            <select
              id={toId}
              className={styles.select}
              value={years.to ?? ""}
              disabled={years.years.length === 0}
              onChange={(event) => change(yearChange(years, "year_to", event.target.value))}
            >
              {years.years
                .filter((year) => years.from === undefined || year >= years.from)
                .map((year) => (
                  <option key={year}>{year}</option>
                ))}
            </select>
          </div>
        </div>
      </fieldset>

      <div className={styles.field}>
        <label htmlFor={countryId} className="field-label">
          Athlete country
        </label>
        <select
          id={countryId}
          className={styles.select}
          value={params.get("country") ?? ""}
          onChange={(event) => change({ country: event.target.value })}
        >
          <option value="">All</option>
          {meta.countries.map((country) => (
            <option key={country}>{country}</option>
          ))}
        </select>
      </div>

      <Segmented
        legend="Technique type"
        term="Technique type"
        options={DOMAINS}
        value={params.get("domain") ?? ""}
        onChange={(value) => change({ domain: value })}
      />

      <fieldset>
        <legend>
          Side
          <InfoTip term="Side" />
        </legend>
        {SIDES.map((side) => (
          <label key={side.value} className={styles.check}>
            <input
              type="checkbox"
              checked={sides.length === 0 || sides.includes(side.value)}
              onChange={(event) => change({ side: sideChange(params, side.value, event.target.checked) })}
            />
            {side.label}
          </label>
        ))}
      </fieldset>

      <hr className={styles.separator} />

      <Segmented
        legend="Count by"
        options={COUNT_BY}
        value={params.get("count_by") ?? meta.defaults.count_by}
        onChange={(value) => change({ count_by: value })}
      />
      <NumberFilter
        label="Min. scores per athlete"
        min={1}
        max={50}
        value={params.get("min_scores_athlete") ?? String(meta.defaults.min_scores_athlete)}
        onCommit={(value) => change({ min_scores_athlete: value })}
      />
      <NumberFilter
        label="Min. scores per technique (repertoire)"
        min={1}
        max={10}
        value={params.get("min_scores_technique") ?? String(meta.defaults.min_scores_technique)}
        onCommit={(value) => change({ min_scores_technique: value })}
      />
      <button type="button" className="btn" onClick={reset}>
        Reset filters
      </button>
    </div>
  );
}
