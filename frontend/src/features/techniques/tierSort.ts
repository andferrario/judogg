import type { ParamChange } from "../../filters/filters";

const DEFAULT_SORT = "share";
const DEFAULT_ORDER = "desc";

type Sort = { sort: string; order: "asc" | "desc" };

export function readSort(params: URLSearchParams): Sort {
  return { sort: params.get("sort") ?? DEFAULT_SORT, order: params.get("order") === "asc" ? "asc" : "desc" };
}

// Like the filters, the default sort is never written in the URL.
export function sortChange(current: Sort, column: string): ParamChange {
  const order = current.sort === column && current.order === "desc" ? "asc" : "desc";
  return { sort: column === DEFAULT_SORT ? null : column, order: order === DEFAULT_ORDER ? null : order };
}
