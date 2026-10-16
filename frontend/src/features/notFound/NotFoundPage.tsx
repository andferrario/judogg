import { Link, useLocation } from "react-router";
import { ErrorNotice } from "../../components/ui/ErrorBox";
import { filterSearch } from "../../filters/filters";

export function NotFoundPage() {
  const { search } = useLocation();
  return (
    <ErrorNotice title="Page not found.">
      <Link to={{ pathname: "/techniques", search: filterSearch(new URLSearchParams(search)) }}>Go to Techniques</Link>
    </ErrorNotice>
  );
}
