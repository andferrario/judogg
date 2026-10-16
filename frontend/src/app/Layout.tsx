import { Outlet } from "react-router";
import { TooltipLayer } from "../components/ui/TooltipLayer";
import { FilterRail } from "../filters/FilterRail";
import { useSaveFilters } from "../filters/useSaveFilters";
import { Header } from "./Header";
import { useScrollToTop } from "./useScrollToTop";
import styles from "./Layout.module.css";

export function Layout() {
  useSaveFilters();
  useScrollToTop();
  return (
    <>
      <Header />
      <div className={styles.shell}>
        <aside className={styles.rail} aria-label="Filters">
          <FilterRail />
        </aside>
        <main className={styles.main}>
          <Outlet />
        </main>
      </div>
      <TooltipLayer />
    </>
  );
}
