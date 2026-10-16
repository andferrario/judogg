import { useEffect, useRef } from "react";
import styles from "./TooltipLayer.module.css";

const TIP_ID = "tip";
const OFFSET = 14;
const MARGIN = 8;

// One tooltip for the whole app: any element with a data-tip attribute gets it, on hover and on focus.
export function TooltipLayer() {
  const tipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tip = tipRef.current;
    if (!tip) return;
    let described: Element | null = null;

    const targetOf = (event: Event) => (event.target instanceof Element ? event.target.closest("[data-tip]") : null);
    const show = (target: Element) => {
      tip.textContent = target.getAttribute("data-tip");
      tip.hidden = false;
    };
    const hide = () => {
      tip.hidden = true;
      described?.removeAttribute("aria-describedby");
      described = null;
    };
    const onPointerOver = (event: PointerEvent) => {
      const target = targetOf(event);
      if (target) show(target);
      else hide();
    };
    const onPointerMove = (event: PointerEvent) => {
      if (tip.hidden) return;
      const right = event.clientX + OFFSET + tip.offsetWidth > window.innerWidth - MARGIN;
      const below = event.clientY + OFFSET + tip.offsetHeight > window.innerHeight - MARGIN;
      tip.style.left = `${right ? event.clientX - tip.offsetWidth - OFFSET : event.clientX + OFFSET}px`;
      tip.style.top = `${below ? event.clientY - tip.offsetHeight - OFFSET : event.clientY + OFFSET}px`;
    };
    const onFocusIn = (event: FocusEvent) => {
      hide();
      const target = targetOf(event);
      if (!target) return;
      show(target);
      target.setAttribute("aria-describedby", TIP_ID);
      described = target;
      const box = target.getBoundingClientRect();
      tip.style.left = `${Math.max(MARGIN, Math.min(box.left, window.innerWidth - tip.offsetWidth - MARGIN))}px`;
      tip.style.top = `${box.bottom + 6}px`;
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") hide();
    };

    document.addEventListener("pointerover", onPointerOver);
    document.addEventListener("pointermove", onPointerMove);
    document.addEventListener("focusin", onFocusIn);
    document.addEventListener("keydown", onKeyDown);
    window.addEventListener("scroll", hide, { passive: true });
    return () => {
      document.removeEventListener("pointerover", onPointerOver);
      document.removeEventListener("pointermove", onPointerMove);
      document.removeEventListener("focusin", onFocusIn);
      document.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("scroll", hide);
    };
  }, []);

  return <div ref={tipRef} id={TIP_ID} role="tooltip" className={styles.tip} hidden />;
}
