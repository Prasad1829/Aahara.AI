import { useLayoutEffect } from "react";
import { useLocation } from "react-router-dom";

export default function ScrollToTop() {
  const { pathname } = useLocation();

  useLayoutEffect(() => {
    const scrollRoot = document.scrollingElement || document.documentElement;

    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
    scrollRoot.scrollTop = 0;
    document.body.scrollTop = 0;

    const frame = window.requestAnimationFrame(() => {
      window.scrollTo({ top: 0, left: 0, behavior: "auto" });
      scrollRoot.scrollTop = 0;
      document.body.scrollTop = 0;
    });

    return () => window.cancelAnimationFrame(frame);
  }, [pathname]);

  return null;
}
