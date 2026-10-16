type PaginationProps = { page: number; pages: number; onPage: (page: number) => void };

export function Pagination({ page, pages, onPage }: PaginationProps) {
  return (
    <nav className="more" aria-label="Pages">
      <button type="button" className="btn" disabled={page <= 1} onClick={() => onPage(page - 1)}>
        ← Previous
      </button>
      <span className="num">
        page {page} of {pages}
      </span>
      <button type="button" className="btn" disabled={page >= pages} onClick={() => onPage(page + 1)}>
        Next →
      </button>
    </nav>
  );
}
