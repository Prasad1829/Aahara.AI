import { motion } from "framer-motion";

export default function FloatingElement({
  children,
  className = "",
  duration = 0.7,
  delay = 0,
  distance = 16,
  loop = false,
}) {
  const animateY = loop ? [distance, -distance, distance] : [distance, 0];
  const transitionY = loop
    ? {
        duration,
        delay,
        repeat: Infinity,
        repeatType: "mirror",
        ease: "easeInOut",
      }
    : {
        duration,
        delay,
        ease: "easeOut",
      };

  return (
    <motion.div
      className={className}
      style={{ willChange: "transform, opacity" }}
      initial={{ opacity: 0, y: distance }}
      animate={{ opacity: 1, y: animateY }}
      transition={{
        opacity: { duration: 0.5, delay },
        y: transitionY,
      }}
    >
      {children}
    </motion.div>
  );
}
