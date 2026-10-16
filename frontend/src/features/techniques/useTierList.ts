import { useTechniques } from "../../api/hooks";
import { useFilters } from "../../filters/useFilters";
import { readSort } from "./tierSort";

const TOP = "15";
const ALL = "200";

export function useTierList() {
  const { filters, params } = useFilters();
  const { sort, order } = readSort(params);
  const all = params.get("all") === "1";
  const query = useTechniques(filters, { sort, order, limit: all ? ALL : TOP });
  return { query, sort, order, all };
}
