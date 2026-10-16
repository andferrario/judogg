import { useEffect } from "react";
import { useLocation } from "react-router";
import { readFilters } from "./filters";
import { saveFilters } from "./persistence";

export function useSaveFilters(): void {
  const { search } = useLocation();
  useEffect(() => saveFilters(readFilters(new URLSearchParams(search))), [search]);
}
