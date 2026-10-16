import { useEffect, useRef } from "react";
import { useLocation } from "react-router";

// A new page starts at the top; a filter or page-parameter change (same path) keeps the scroll position.
export function useScrollToTop(): void {
  const { pathname } = useLocation();
  const previous = useRef(pathname);
  useEffect(() => {
    if (previous.current === pathname) return;
    previous.current = pathname;
    window.scrollTo(0, 0);
  }, [pathname]);
}
