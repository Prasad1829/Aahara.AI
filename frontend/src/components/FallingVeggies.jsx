import { motion } from "framer-motion";

const particles = [
  "bg-blue-200",
  "bg-cyan-200",
  "bg-emerald-200",
  "bg-sky-200",
  "bg-teal-200",
  "bg-indigo-200",
];

export default function FallingVeggies() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {particles.map((color, index) => (
        <motion.div
          key={index}
          initial={{ y: -100, x: Math.random() * window.innerWidth }}
          animate={{ y: "110vh" }}
          transition={{
            duration: 9 + Math.random() * 6,
            repeat: Infinity,
            delay: index * 0.6,
          }}
          className={`absolute h-10 w-10 rounded-full opacity-40 blur-[1px] ${color}`}
        />
      ))}
    </div>
  );
}
