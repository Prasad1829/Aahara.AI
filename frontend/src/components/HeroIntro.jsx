import { motion } from "framer-motion";

export default function HeroIntro({ userEmail, onStart }) {
  const heroVeggies = [
    { name: "Tomato", src: "/vegetables/tomato.jpg" },
    { name: "Carrot", src: "/vegetables/carrot.jpg" },
    { name: "Onion", src: "/vegetables/onion.jpg" },
    { name: "Capsicum", src: "/vegetables/capsicum.jpg" },
  ];

  return (
    <div className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_10%_10%,#fde68a,transparent_35%),radial-gradient(circle_at_95%_5%,#99f6e4,transparent_30%),linear-gradient(150deg,#f8fafc,#e2e8f0_45%,#dbeafe)] px-4 py-8">
      <div className="pointer-events-none absolute inset-0 opacity-50">
        <motion.div
          className="absolute left-10 top-20 h-24 w-24 rounded-full bg-amber-300/40 blur-xl"
          animate={{ y: [0, -16, 0] }}
          transition={{ duration: 4.2, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-16 right-14 h-28 w-28 rounded-full bg-cyan-400/35 blur-xl"
          animate={{ y: [0, 14, 0] }}
          transition={{ duration: 3.8, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      <div className="relative z-10 mx-auto flex min-h-[88vh] max-w-6xl items-center">
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full rounded-3xl border border-slate-200/80 bg-white/70 p-5 shadow-2xl backdrop-blur-xl md:p-10"
        >
          <div className="grid items-center gap-8 md:grid-cols-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-700">
                Welcome {userEmail ? userEmail : "Chef"}
              </p>
              <h1 className="mt-3 text-4xl font-black leading-tight text-slate-900 md:text-6xl">
                Cook Smarter with <span className="text-blue-700">AHARA.AI</span>
              </h1>
              <div className="mt-6 grid gap-2 text-sm text-slate-700">
                <p className="rounded-lg border border-slate-200 bg-white/80 px-3 py-2">1. Upload ingredient image</p>
                <p className="rounded-lg border border-slate-200 bg-white/80 px-3 py-2">2. AI detects ingredients</p>
                <p className="rounded-lg border border-slate-200 bg-white/80 px-3 py-2">3. Get best recipe suggestions</p>
              </div>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={onStart}
                className="mt-7 min-h-12 rounded-xl bg-gradient-to-r from-amber-300 to-cyan-300 px-8 py-3 text-base font-black text-zinc-900 transition hover:brightness-105"
              >
                Start with AHARA
              </motion.button>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white/75 p-4">
              <p className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-700">Visual Ingredient Cue</p>
              <div className="mt-4 grid grid-cols-2 gap-3">
                {heroVeggies.map((item, idx) => (
                  <motion.div
                    key={item.name}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: idx * 0.08 }}
                    className="overflow-hidden rounded-xl border border-white/15 bg-zinc-900"
                  >
                    <img src={item.src} alt={item.name} className="h-24 w-full object-cover md:h-28" />
                    <p className="px-2 py-1 text-xs font-semibold text-zinc-100">{item.name}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </motion.section>
      </div>
    </div>
  );
}
