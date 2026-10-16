import { Link } from "react-router";
import type { Athlete, TechniqueRef } from "../../api/types";
import { useFilterSearch } from "../../filters/useFilterSearch";
import { athleteName } from "../../format/format";

export function TechniqueLink({ technique }: { technique: TechniqueRef | null }) {
  const search = useFilterSearch();
  if (technique === null) return <span className="dim">Unknown technique</span>;
  return (
    <Link className="tlink" to={{ pathname: `/techniques/${technique.code}`, search }}>
      {technique.name}
    </Link>
  );
}

export function AthleteLink({ athlete }: { athlete: Athlete }) {
  const search = useFilterSearch();
  return (
    <>
      <Link className="tlink" to={{ pathname: `/athletes/${athlete.id}`, search }}>
        {athleteName(athlete)}
      </Link>{" "}
      <span className="cc">{athlete.country_code}</span>
    </>
  );
}

export function BackToTechniques() {
  const search = useFilterSearch();
  return (
    <Link className="tlink" to={{ pathname: "/techniques", search }}>
      ← Techniques
    </Link>
  );
}
