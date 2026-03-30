import { memo } from "react";
import { motion } from "framer-motion";

function CircularSlider({
  items,
  selectedItems = [],
  onToggleItem,
  className = "",
  duration = 34,
}) {
  return (
    <div
      className={`relative mx-auto aspect-square w-full max-w-[420px] ${className}`}
      style={
        {
          "--orbit-size": "clamp(260px, 72vw, 420px)",
          "--orbit-radius": "clamp(96px, 27vw, 150px)",
          "--item-size": "clamp(56px, 12vw, 78px)",
        }
      }
    >
      <div
        className="absolute inset-0 rounded-full"
        style={{
          backgroundColor: "#bc8b5a",
          backgroundImage:
            "repeating-linear-gradient(35deg, #c69767 0 8px, #b78758 8px 16px, #c19162 16px 24px)",
          boxShadow: "inset 0 10px 18px rgba(0,0,0,0.24), inset 0 -4px 8px rgba(255,255,255,0.05)",
        }}
      />
      <div className="absolute inset-[19%] rounded-full bg-[#0f0f0f]" />

      <motion.div
        className="absolute inset-0"
        animate={{ rotate: 360 }}
        transition={{ duration, ease: "linear", repeat: Infinity }}
        style={{ willChange: "transform" }}
      >
        {items.map((item, index) => {
          const angle = (360 / items.length) * index;
          const selected = selectedItems.includes(item.name);
          return (
            <div
              key={item.name}
              className="absolute left-1/2 top-1/2"
              style={{
                transform: `translate(-50%, -50%) rotate(${angle}deg) translateY(calc(-1 * var(--orbit-radius)))`,
              }}
            >
              <motion.button
                onClick={() => onToggleItem(item.name)}
                className={`grid place-items-center rounded-full border-2 ${
                  selected ? "border-amber-400" : "border-white/80"
                } bg-black/20 p-1.5`}
                style={{
                  width: "var(--item-size)",
                  height: "var(--item-size)",
                  boxShadow: "0 5px 10px rgba(0,0,0,0.35)",
                }}
                whileTap={{ scale: 0.95 }}
              >
                <motion.div
                  animate={{ rotate: -360 }}
                  transition={{ duration, ease: "linear", repeat: Infinity }}
                  style={{ willChange: "transform" }}
                  className="h-full w-full"
                >
                  <img
                    src={item.src}
                    alt={item.name}
                    loading="lazy"
                    className="h-full w-full rounded-full object-cover"
                  />
                </motion.div>
              </motion.button>
            </div>
          );
        })}
      </motion.div>
    </div>
  );
}

export default memo(CircularSlider);
