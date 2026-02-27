import { memo } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Heart } from "lucide-react";
import AnimatedCard from "./AnimatedCard";

const RecipeItem = memo(function RecipeItem({ recipe, recipeKey, isSaved, onToggleSave, delay }) {
  const scorePct = Math.round((recipe.match_score || 0) * 100);

  return (
    <AnimatedCard delay={delay} className="p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-xl font-extrabold text-stone-900">{recipe.name}</h3>
          <p className="mt-1 text-sm text-stone-600">
            {recipe.is_veg ? "Veg" : "Non-Veg"} · {recipe.cooking_time_minutes} mins
          </p>
        </div>

        <motion.button
          onClick={() => onToggleSave?.(recipeKey)}
          whileTap={{ scale: 0.85 }}
          animate={isSaved ? { scale: [1, 1.2, 1] } : { scale: 1 }}
          transition={{ duration: 0.25 }}
          className={`min-h-11 min-w-11 rounded-full border p-2 ${
            isSaved ? "border-rose-300 bg-rose-50 text-rose-600" : "border-stone-200 bg-white text-stone-500"
          }`}
          aria-label={isSaved ? "Unsave recipe" : "Save recipe"}
          style={{ willChange: "transform, opacity" }}
        >
          <Heart size={18} fill={isSaved ? "currentColor" : "none"} />
        </motion.button>
      </div>

      <div className="mt-4">
        <div className="mb-1 flex justify-between text-sm text-stone-700">
          <span className="font-semibold">Ingredient Match</span>
          <span className="font-bold">{scorePct}%</span>
        </div>
        <div className="h-2.5 overflow-hidden rounded-full bg-stone-200">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-green-400"
            initial={{ scaleX: 0, transformOrigin: "left center" }}
            animate={{ scaleX: Math.max(0.02, scorePct / 100) }}
            transition={{ duration: 0.7, delay: delay + 0.08 }}
            style={{ willChange: "transform, opacity" }}
          />
        </div>
      </div>

      <div className="mt-3 text-sm text-stone-700">
        <p>
          <span className="font-semibold">Matched:</span> {recipe.matched_ingredients.join(", ") || "-"}
        </p>
      </div>

      <div className="mt-2">
        <p className="mb-1 text-sm font-semibold text-stone-800">Missing</p>
        <div className="flex flex-wrap gap-1.5">
          {recipe.missing_ingredients?.length > 0 ? (
            recipe.missing_ingredients.map((item, idx) => (
              <motion.span
                key={`${item}-${idx}`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, delay: delay + idx * 0.03 }}
                className="inline-flex items-center rounded-full border border-rose-300 bg-rose-50 px-2.5 py-1 text-xs font-medium text-rose-700"
                style={{ willChange: "transform, opacity" }}
              >
                {item}
              </motion.span>
            ))
          ) : (
            <span className="text-sm text-emerald-700">No missing ingredients</span>
          )}
        </div>
      </div>

      {recipe.instructions?.length > 0 && (
        <div className="mt-4">
          <p className="font-bold text-stone-900">Instructions</p>
          <ol className="mt-1 list-inside list-decimal space-y-1 text-sm text-stone-700">
            {recipe.instructions.map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ol>
        </div>
      )}
    </AnimatedCard>
  );
});

export default function RecipeList({ recommended_recipes, blockKey, savedRecipes, onToggleSave }) {
  const recipes = recommended_recipes || [];

  return (
    <>
      <h2 className="mb-3 mt-6 text-lg font-bold text-stone-900">Recommended Recipes</h2>
      {recipes.length === 0 && <p className="text-stone-600">No recipe matches found. Try another image.</p>}

      <div className="space-y-4">
        <AnimatePresence>
          {recipes.map((recipe, index) => {
            const recipeKey = `${blockKey}-${recipe.name}-${index}`;
            return (
              <motion.div
                key={recipeKey}
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.28, delay: index * 0.05 }}
                style={{ willChange: "transform, opacity" }}
              >
                <RecipeItem
                  recipe={recipe}
                  recipeKey={recipeKey}
                  isSaved={savedRecipes?.includes(recipeKey)}
                  onToggleSave={onToggleSave}
                  delay={index * 0.04}
                />
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </>
  );
}
