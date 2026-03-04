import { memo } from "react";
import { motion } from "framer-motion";

function SmokeTransition({ active = true, onComplete }) {
  if (!active) return null;

  return (
    <motion.div
      aria-hidden="true"
      className="pointer-events-none absolute z-10"
      style={{
        left: "-20%",
        top: "-20%",
        width: "140%",
        height: "140%",
        willChange: "transform, opacity",
      }}
      initial={{ x: "0%", y: "0%", opacity: 0, scale: 1 }}
      animate={{
        x: "40%",
        y: "40%",
        opacity: [0, 0.45, 0],
        scale: 1.2,
      }}
      transition={{ duration: 1.2, ease: "easeInOut" }}
      onAnimationComplete={onComplete}
    >
      <div className="relative h-full w-full">
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background:
              "radial-gradient(circle at 35% 35%, rgba(255,255,255,0.36) 0%, rgba(255,255,255,0.14) 40%, rgba(255,255,255,0) 72%)",
            filter: "blur(10px)",
          }}
        />
        <div
          className="absolute inset-[12%] rounded-full"
          style={{
            background:
              "radial-gradient(circle at 60% 55%, rgba(220,220,220,0.28) 0%, rgba(220,220,220,0.12) 38%, rgba(220,220,220,0) 72%)",
            filter: "blur(8px)",
          }}
        />
      </div>
    </motion.div>
  );
}

export default memo(SmokeTransition);
