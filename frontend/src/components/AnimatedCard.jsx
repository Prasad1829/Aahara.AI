import { motion } from "framer-motion";

export default function AnimatedCard({ children, className = "", delay = 0 }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay, ease: "easeOut" }}
      whileHover={{ y: -6 }}
      className={`rounded-2xl border border-white/50 bg-white/80 shadow-lg backdrop-blur-md ${className}`}
      style={{ willChange: "transform, opacity" }}
    >
      {children}
    </motion.article>
  );
}
