import { Link, NavLink, useLocation } from "react-router";
import { filterSearch } from "../filters/filters";
import { Search } from "../search/Search";
import styles from "./Header.module.css";

const SECTIONS = [
  { path: "/techniques", label: "Techniques" },
  { path: "/repertoire", label: "Repertoire" },
  { path: "/penalties", label: "Penalties" },
  { path: "/coverage", label: "Coverage" },
];

export function Header() {
  const search = filterSearch(new URLSearchParams(useLocation().search));
  return (
    <header className={styles.top}>
      <Link className={styles.brand} to={{ pathname: "/techniques", search }}>
        <i className={styles.mark} aria-hidden="true" />
        Judogg
      </Link>
      <nav className={styles.nav} aria-label="Sections">
        {SECTIONS.map(({ path, label }) => (
          <NavLink key={path} to={{ pathname: path, search }}>
            {label}
          </NavLink>
        ))}
      </nav>
      <Search />
    </header>
  );
}
