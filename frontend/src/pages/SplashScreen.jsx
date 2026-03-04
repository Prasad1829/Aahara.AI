import { useEffect, useState } from "react";

export default function SplashScreen({ onDone }) {
  const [phase, setPhase] = useState("hidden"); // hidden -> visible -> fadeout

  useEffect(() => {
    // Total splash time ~1500ms
    const showTimer = setTimeout(() => setPhase("visible"), 450);
    const fadeTimer = setTimeout(() => setPhase("fadeout"), 1200);
    const doneTimer = setTimeout(() => onDone?.(), 1500);

    return () => {
      clearTimeout(showTimer);
      clearTimeout(fadeTimer);
      clearTimeout(doneTimer);
    };
  }, [onDone]);

  const isVisible = phase === "visible";
  const isFadingOut = phase === "fadeout";

  return (
    <div
      style={{
        height: "100vh",
        width: "100vw",
        overflow: "hidden",
        background: "#0F766E",
      }}
    >
      <div
        style={{
          height: "100%",
          width: "100%",
          opacity: isFadingOut ? 0 : 1,
          transition: "opacity 450ms ease-out",
        }}
      >
        <div
          style={{
            height: "100%",
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <img
            src="/splash-logo.png"
            alt="Aahara logo"
            style={{
              width: 180,
              height: 180,
              objectFit: "contain",
              userSelect: "none",
              opacity: isVisible ? 1 : 0,
              transform: `scale(${isVisible ? 1 : 0.9})`,
              transition: "opacity 520ms ease-out, transform 520ms ease-out",
            }}
            draggable={false}
          />
        </div>
      </div>
    </div>
  );
}
