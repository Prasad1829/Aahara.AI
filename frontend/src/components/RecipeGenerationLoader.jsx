import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ChefHat, ScanSearch, Sparkles, Soup } from "lucide-react";

const DEFAULT_STEPS = [
  { label: "Reading ingredients", Icon: ScanSearch },
  { label: "Matching recipes", Icon: Sparkles },
  { label: "Preparing your results", Icon: Soup },
];

export default function RecipeGenerationLoader({
  title = "Generating recipes",
  description = "This usually takes a few seconds.",
  steps = DEFAULT_STEPS,
  accent = "#4a9e6b",
  compact = false,
}) {
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    if (steps.length <= 1) return undefined;

    const intervalId = window.setInterval(() => {
      setActiveIndex((current) => (current + 1) % steps.length);
    }, 1300);

    return () => window.clearInterval(intervalId);
  }, [steps.length]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="recipe-loader-card"
      style={{
        marginTop: compact ? 14 : 18,
        padding: compact ? "16px 18px" : "18px 20px",
        borderRadius: 18,
        border: `1px solid ${accent}33`,
        background: "rgba(255,255,255,0.82)",
        boxShadow: "0 18px 40px -30px rgba(15,23,42,0.55)",
        backdropFilter: "blur(12px)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2.4, ease: "linear", repeat: Infinity }}
          style={{
            width: compact ? 42 : 48,
            height: compact ? 42 : 48,
            borderRadius: "50%",
            flexShrink: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: `linear-gradient(135deg, ${accent}, #f4b266)`,
            color: "#fff",
            boxShadow: `0 10px 24px -18px ${accent}`,
          }}
        >
          <ChefHat size={compact ? 18 : 20} />
        </motion.div>

        <div style={{ minWidth: 0, flex: 1 }}>
          <p style={{ margin: 0, fontSize: compact ? "0.94rem" : "1rem", fontWeight: 800, color: "#1f2937" }}>
            {title}
          </p>
          <p style={{ margin: "4px 0 0", fontSize: "0.82rem", color: "#6b7280" }}>
            {description}
          </p>
        </div>
      </div>

      <div className="recipe-loader-track" style={{ marginTop: compact ? 14 : 16 }}>
        <motion.div
          className="recipe-loader-sweep"
          animate={{ x: ["-38%", "118%"] }}
          transition={{ duration: 1.5, ease: "easeInOut", repeat: Infinity }}
          style={{ background: `linear-gradient(90deg, transparent, ${accent}, transparent)` }}
        />
      </div>

      <div
        style={{
          marginTop: compact ? 12 : 14,
          display: "grid",
          gridTemplateColumns: compact ? "1fr" : "repeat(3, minmax(0, 1fr))",
          gap: 10,
        }}
      >
        {steps.map(({ label, Icon }, index) => {
          const isActive = index === activeIndex;
          return (
            <motion.div
              key={label}
              animate={isActive ? { y: [0, -2, 0] } : { y: 0 }}
              transition={{ duration: 0.9, repeat: isActive ? Infinity : 0 }}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 9,
                borderRadius: 14,
                padding: compact ? "10px 12px" : "11px 12px",
                border: `1px solid ${isActive ? `${accent}44` : "rgba(148,163,184,0.18)"}`,
                background: isActive ? `${accent}14` : "rgba(248,250,252,0.72)",
                color: isActive ? accent : "#475569",
              }}
            >
              <Icon size={16} />
              <span style={{ fontSize: "0.8rem", fontWeight: isActive ? 700 : 600 }}>
                {label}
              </span>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
