import type { ReactNode } from "react";
import { Link, useLocation } from "react-router";
import { ApiError } from "../../api/client";
import { filterSearch, resetFilters, toSearch } from "../../filters/filters";
import styles from "./ErrorBox.module.css";

type ErrorBoxProps = { error: Error; onRetry?: () => void; retrying?: boolean };

export function ErrorBox({ error, onRetry, retrying = false }: ErrorBoxProps) {
  const { pathname, search } = useLocation();
  const params = new URLSearchParams(search);
  if (error instanceof ApiError && error.code === "invalid_parameter") {
    return (
      <ErrorNotice title="Invalid filters." message={error.message}>
        <Link replace to={{ pathname, search: toSearch(resetFilters(params)) }}>
          Reset filters
        </Link>
      </ErrorNotice>
    );
  }
  if (error instanceof ApiError && error.code === "not_found") {
    return (
      <ErrorNotice title="Not found." message={error.message}>
        <Link to={{ pathname: "/techniques", search: filterSearch(params) }}>Go to Techniques</Link>
      </ErrorNotice>
    );
  }
  return (
    <ErrorNotice title="Something went wrong." message="The data could not be loaded.">
      {onRetry && (
        <button type="button" className="btn" onClick={onRetry} disabled={retrying}>
          {retrying ? "Retrying…" : "Retry"}
        </button>
      )}
    </ErrorNotice>
  );
}

type ErrorNoticeProps = { title: string; message?: string; children?: ReactNode };

export function ErrorNotice({ title, message, children }: ErrorNoticeProps) {
  return (
    <div className={styles.box} role="alert">
      <p className={styles.text}>
        <strong>{title}</strong> {message}
      </p>
      {children}
    </div>
  );
}
