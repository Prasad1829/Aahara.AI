import { useEffect, useState } from "react";
import { motion } from "framer-motion";

const BRAND_GREEN = "#2E8B57";
const LOGO_DURATION_MS = 1500;
const GREEN_ONLY_MS = 1000;
const TYPE_DURATION_MS = 1000;
const WAIT_AFTER_TYPE_MS = 1000;
const FADE_OUT_MS = 350;

export default function SplashScreen({ onDone }) {
  const [phase, setPhase] = useState("green");
  const [typedText, setTypedText] = useState("");
  const fullTitle = "Aahara.AI";
  const typeSpeedMs = Math.max(30, Math.floor(TYPE_DURATION_MS / fullTitle.length));

  useEffect(() => {
    if (phase !== "green") return;
    const timer = setTimeout(() => setPhase("logo"), GREEN_ONLY_MS);
    return () => clearTimeout(timer);
  }, [phase]);

  useEffect(() => {
    if (phase !== "logo") return;
    const timer = setTimeout(() => setPhase("typing"), LOGO_DURATION_MS);
    return () => clearTimeout(timer);
  }, [phase]);

  useEffect(() => {
    if (phase !== "typing") return;
    let index = 0;
    const interval = setInterval(() => {
      index += 1;
      setTypedText(fullTitle.slice(0, index));
      if (index >= fullTitle.length) {
        clearInterval(interval);
        setPhase("wait");
      }
    }, typeSpeedMs);
    return () => clearInterval(interval);
  }, [phase, typeSpeedMs, fullTitle]);

  useEffect(() => {
    if (phase !== "wait") return;
    const delay = Math.max(0, WAIT_AFTER_TYPE_MS - FADE_OUT_MS);
    const timer = setTimeout(() => setPhase("fade"), delay);
    return () => clearTimeout(timer);
  }, [phase, onDone]);

  useEffect(() => {
    if (phase !== "fade") return;
    const timer = setTimeout(() => onDone?.(), FADE_OUT_MS);
    return () => clearTimeout(timer);
  }, [phase, onDone]);

  return (
    <motion.div
      initial={{ opacity: 1 }}
      animate={{ opacity: phase === "fade" ? 0 : 1 }}
      transition={{ duration: FADE_OUT_MS / 1000, ease: "easeOut" }}
      style={{
        height: "100vh",
        width: "100%",
        overflow: "hidden",
        background: BRAND_GREEN,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
        gap: 14,
      }}
    >
      {phase !== "green" && (
        <>
          <motion.div
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: LOGO_DURATION_MS / 1000, ease: "easeOut" }}
            style={{
              background: "#ffffff",
              borderRadius: 24,
              padding: 16,
              boxShadow: "0 16px 36px rgba(0,0,0,0.2)",
              display: "grid",
              placeItems: "center",
            }}
          >
            <img
              src="/splash-logo.png"
              alt="Aahara logo"
              style={{
                width: 160,
                height: 160,
                objectFit: "contain",
                userSelect: "none",
              }}
              draggable={false}
            />
          </motion.div>

          <div
            style={{
              minHeight: 42,
              fontFamily: "'Playfair Display', serif",
              fontWeight: 900,
              fontSize: "2.2rem",
              color: "#ffffff",
              letterSpacing: "0.4px",
              textAlign: "center",
            }}
          >
            {phase === "typing" || phase === "wait" ? typedText : ""}
          </div>
        </>
      )}
    </motion.div>
  );
}
