import { motion } from "framer-motion";

export default function LoadingButton({
  onClick,
  loading = false,
  disabled = false,
  label = "Submit",
  loadingLabel = "Loading...",
  className = "",
  spinnerClassName = "",
  type = "button",
}) {
  const blocked = loading || disabled;

  return (
    <motion.button
      whileHover={!blocked ? { scale: 1.02 } : {}}
      whileTap={!blocked ? { scale: 0.98 } : {}}
      onClick={onClick}
      type={type}
      disabled={blocked}
      className={`motion-btn inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-5 py-2.5 font-semibold transition disabled:cursor-not-allowed disabled:opacity-60 ${className}`}
      style={{ willChange: "transform, opacity" }}
    >
      {loading && <span className={`spinner ${spinnerClassName}`} />}
      <span>{loading ? loadingLabel : label}</span>
    </motion.button>
  );
}
