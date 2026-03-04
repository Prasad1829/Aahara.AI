import { memo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Heart, Clock, Leaf, FlameKindling, ChevronDown, CheckCircle2, AlertCircle } from "lucide-react";

function ScoreRing({ pct, delay }) {
  const r = 28;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  const color = pct >= 80 ? "#16a34a" : pct >= 50 ? "#d97706" : "#dc2626";

  return (
    <div className="relative flex h-16 w-16 items-center justify-center">
      <svg width="64" height="64" className="-rotate-90">
        <circle cx="32" cy="32" r={r} fill="none" stroke="#e7e5e4" strokeWidth="5" />
        <motion.circle
          cx="32" cy="32" r={r} fill="none"
          stroke={color} strokeWidth="5" strokeLinecap="round"
          strokeDasharray={`${circ}`}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: circ - dash }}
          transition={{ duration: 1, delay: delay + 0.2, ease: "easeOut" }}
        />
      </svg>
      <span className="absolute text-sm font-black" style={{ color, fontFamily: "'Playfair Display', Georgia, serif" }}>
        {pct}%
      </span>
    </div>
  );
}

const RecipeCard = memo(function RecipeCard({ recipe, recipeKey, isSaved, onToggleSave, delay = 0 }) {
  const [open, setOpen] = useState(false);
  const scorePct = Math.round((recipe.match_score || 0) * 100);
  const isVeg = recipe.is_veg;

  return (
    <motion.article
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.38, delay, ease: "easeOut" }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className="overflow-hidden rounded-3xl"
      style={{
        background: "linear-gradient(160deg, #fffbf2 0%, #f7f3ea 100%)",
        border: "1px solid rgba(199,119,44,0.18)",
        boxShadow: "0 8px 32px -8px rgba(139,69,19,0.14), 0 2px 8px -2px rgba(0,0,0,0.06)",
        willChange: "transform",
      }}
    >
      <div className="h-1" style={{ background: isVeg ? "linear-gradient(90deg, #6ee7b7, #34d399, #6ee7b7)" : "linear-gradient(90deg, #fca5a5, #f87171, #fca5a5)" }} />

      <div className="p-6 md:p-7">
        <div className="flex items-start gap-4">
          <ScoreRing pct={scorePct} delay={delay} />

          <div className="flex-1 min-w-0">
            <h3 className="text-2xl font-black leading-tight text-stone-900 md:text-3xl" style={{ fontFamily: "'Playfair Display', Georgia, serif" }}>
              {recipe.name}
            </h3>
            <div className="mt-2 flex flex-wrap items-center gap-3">
              <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wide ${isVeg ? "bg-emerald-100 text-emerald-800 border border-emerald-200" : "bg-rose-50 text-rose-700 border border-rose-200"}`}>
                {isVeg ? <Leaf size={11} /> : <FlameKindling size={11} />}
                {isVeg ? "Vegetarian" : "Non-Veg"}
              </span>
              {recipe.cooking_time_minutes && (
                <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-stone-500">
                  <Clock size={12} className="text-amber-600" />
                  {recipe.cooking_time_minutes} mins
                </span>
              )}
            </div>
          </div>

          <motion.button
            onClick={() => onToggleSave?.(recipeKey)}
            whileTap={{ scale: 0.8 }}
            animate={isSaved ? { scale: [1, 1.3, 1] } : { scale: 1 }}
            transition={{ duration: 0.3 }}
            className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full border-2 transition-colors duration-200 ${isSaved ? "border-rose-300 bg-rose-50 text-rose-500" : "border-stone-200 bg-white text-stone-400 hover:border-rose-200 hover:text-rose-400"}`}
            aria-label={isSaved ? "Unsave recipe" : "Save recipe"}
          >
            <Heart size={17} fill={isSaved ? "currentColor" : "none"} />
          </motion.button>
        </div>

        <div className="my-5 h-px bg-gradient-to-r from-amber-200/60 via-stone-200 to-transparent" />

        {recipe.matched_ingredients?.length > 0 && (
          <div className="mb-4">
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.14em] text-stone-400" style={{ fontFamily: "'Lora', Georgia, serif" }}>Matched Ingredients</p>
            <div className="flex flex-wrap gap-2">
              {recipe.matched_ingredients.map((item, idx) => (
                <motion.span key={`match-${item}-${idx}`} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.22, delay: delay + idx * 0.04 }} className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800">
                  <CheckCircle2 size={10} className="text-emerald-500" />{item}
                </motion.span>
              ))}
            </div>
          </div>
        )}

        {recipe.missing_ingredients?.length > 0 && (
          <div className="mb-4">
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.14em] text-stone-400" style={{ fontFamily: "'Lora', Georgia, serif" }}>You'll Need</p>
            <div className="flex flex-wrap gap-2">
              {recipe.missing_ingredients.map((item, idx) => (
                <motion.span key={`miss-${item}-${idx}`} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.22, delay: delay + idx * 0.04 }} className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800">
                  <AlertCircle size={10} className="text-amber-500" />{item}
                </motion.span>
              ))}
            </div>
          </div>
        )}

        {recipe.missing_ingredients?.length === 0 && (
          <div className="mb-4 flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-2.5">
            <CheckCircle2 size={15} className="text-emerald-600" />
            <span className="text-sm font-semibold text-emerald-800">You have all ingredients!</span>
          </div>
        )}

        {recipe.instructions?.length > 0 && (
          <div className="mt-2">
            <button onClick={() => setOpen((v) => !v)} className="flex w-full items-center justify-between rounded-2xl border border-stone-200 bg-white/70 px-4 py-3 text-sm font-bold text-stone-700 transition-colors hover:bg-white">
              <span style={{ fontFamily: "'Lora', Georgia, serif" }}>Cooking Instructions ({recipe.instructions.length} steps)</span>
              <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.22 }}>
                <ChevronDown size={16} className="text-amber-600" />
              </motion.div>
            </button>

            <AnimatePresence>
              {open && (
                <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.28, ease: "easeInOut" }} className="overflow-hidden">
                  <ol className="mt-3 space-y-3 px-1">
                    {recipe.instructions.map((step, idx) => (
                      <motion.li key={idx} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.2, delay: idx * 0.05 }} className="flex gap-3">
                        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-black text-white" style={{ background: "linear-gradient(135deg, #C7772C, #e09040)" }}>
                          {idx + 1}
                        </span>
                        <p className="flex-1 pt-0.5 text-sm leading-relaxed text-stone-600" style={{ fontFamily: "'Lora', Georgia, serif" }}>{step}</p>
                      </motion.li>
                    ))}
                  </ol>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </motion.article>
  );
});

export default RecipeCard;