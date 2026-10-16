import { useLocation } from "react-router";
import { filterSearch } from "./filters";

export function useFilterSearch(extra: Record<string, string> = {}): string {
  return filterSearch(new URLSearchParams(useLocation().search), extra);
}
