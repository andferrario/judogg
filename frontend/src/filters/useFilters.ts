import { useLocation, useNavigate } from "react-router";
import { useMetaData } from "../app/meta";
import {
  changeFilters,
  changeParams,
  readFilters,
  resetFilters,
  toSearch,
  type FilterChange,
  type ParamChange,
} from "./filters";

export function useFilters() {
  const { pathname, search } = useLocation();
  const navigate = useNavigate();
  const { defaults } = useMetaData();
  const params = new URLSearchParams(search);
  // A filter click replaces the history entry: Back leaves the page instead of undoing every click.
  const replace = (next: URLSearchParams) => navigate({ pathname, search: toSearch(next) }, { replace: true });
  return {
    params,
    filters: readFilters(params),
    change: (change: FilterChange) => void replace(changeFilters(params, change, defaults)),
    reset: () => void replace(resetFilters(params)),
    setPageParams: (change: ParamChange) => void replace(changeParams(params, change)),
  };
}
