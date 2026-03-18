import { motion } from "framer-motion";
import { ArrowRight, ChefHat, Clock, Flame, Leaf, PlusCircle } from "lucide-react";
import RecipeImage from "./RecipeImage";

export default function RecipeRecommendationSection({
  title,
  recipes,
  ingredientsFallback = [],
  onRecipeClick,
  variant = "recommended",
  cardStyle,
}) {
  if (!recipes?.length) {
    return null;
  }

  const isAdditional = variant === "additional";
  const visibleRecipes = isAdditional ? recipes.slice(0, 3) : recipes;
  const accentColor = isAdditional ? "#4a9e6b" : "#C8873A";
  const accentBorder = isAdditional ? "rgba(74,158,107,0.3)" : "rgba(200,135,58,0.3)";
  const cardBackground = isAdditional ? "rgba(74,158,107,0.06)" : "rgba(200,135,58,0.06)";
  const cardHoverBackground = isAdditional ? "rgba(74,158,107,0.12)" : "rgba(200,135,58,0.12)";
  const cardBorder = isAdditional ? "rgba(74,158,107,0.2)" : "rgba(200,135,58,0.2)";
  const cardHoverBorder = isAdditional ? "rgba(74,158,107,0.45)" : "rgba(200,135,58,0.45)";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ ...cardStyle, border: `1px solid ${accentBorder}`, marginBottom: 14 }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        {isAdditional ? <PlusCircle size={16} color={accentColor} /> : <ChefHat size={16} color={accentColor} />}
        <span style={{ fontWeight: 700, color: accentColor, fontSize: "0.9rem" }}>
          {title} ({visibleRecipes.length})
        </span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {visibleRecipes.map((recipe, i) => {
          const clickable = typeof onRecipeClick === "function";
          return (
            <motion.div
              key={`${recipe.name || "recipe"}-${i}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              whileHover={clickable ? { x: 4 } : undefined}
              whileTap={clickable ? { scale: 0.99 } : undefined}
              onClick={clickable ? () => onRecipeClick(recipe) : undefined}
              style={{
                padding: "12px 14px",
                borderRadius: 12,
                cursor: clickable ? "pointer" : "default",
                background: cardBackground,
                border: `1px solid ${cardBorder}`,
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                if (!clickable) return;
                e.currentTarget.style.background = cardHoverBackground;
                e.currentTarget.style.border = `1px solid ${cardHoverBorder}`;
              }}
              onMouseLeave={(e) => {
                if (!clickable) return;
                e.currentTarget.style.background = cardBackground;
                e.currentTarget.style.border = `1px solid ${cardBorder}`;
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1 }}>
                  <RecipeImage
                    name={recipe.name || recipe}
                    ingredients={recipe.ingredients || recipe.matched_ingredients || ingredientsFallback}
                    imageUrl={recipe.image_url}
                    imageFallbackUrl={recipe.image_fallback_url}
                    alt={recipe.name || recipe}
                    style={{ width: 48, height: 48, borderRadius: 10, objectFit: "cover", flexShrink: 0 }}
                    loading="lazy"
                  />
                  <div style={{ flex: 1 }}>
                    <h3 style={{ fontWeight: 700, color: "#2d2d2d", fontSize: "0.88rem", marginBottom: 5 }}>
                      {recipe.name || recipe}
                    </h3>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginBottom: isAdditional ? 6 : 0 }}>
                      {recipe.is_veg !== undefined && (
                        <span
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 4,
                            padding: "2px 8px",
                            borderRadius: 20,
                            fontSize: "0.68rem",
                            fontWeight: 600,
                            background: recipe.is_veg ? "rgba(74,158,107,0.12)" : "rgba(239,68,68,0.1)",
                            color: recipe.is_veg ? "#2d6a4a" : "#dc2626",
                            border: `1px solid ${recipe.is_veg ? "rgba(74,158,107,0.3)" : "rgba(239,68,68,0.25)"}`,
                          }}
                        >
                          {recipe.is_veg ? <Leaf size={10} /> : <Flame size={10} />}
                          {recipe.is_veg ? "Veg" : "Non-Veg"}
                        </span>
                      )}
                      {recipe.cooking_time_minutes && (
                        <span
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 4,
                            padding: "2px 8px",
                            borderRadius: 20,
                            fontSize: "0.68rem",
                            fontWeight: 600,
                            background: isAdditional ? "rgba(74,158,107,0.1)" : "rgba(200,135,58,0.1)",
                            color: accentColor,
                            border: `1px solid ${isAdditional ? "rgba(74,158,107,0.25)" : "rgba(200,135,58,0.25)"}`,
                          }}
                        >
                          <Clock size={10} /> {recipe.cooking_time_minutes} min
                        </span>
                      )}
                    </div>

                    {isAdditional && (
                      <div style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.76rem", color: "#4b5563" }}>
                        <p style={{ margin: 0 }}>
                          <span style={{ fontWeight: 700, color: "#2d6a4a" }}>You have:</span>{" "}
                          {(recipe.matched_ingredients || []).join(", ") || "-"}
                        </p>
                        <p style={{ margin: 0 }}>
                          <span style={{ fontWeight: 700, color: "#b45309" }}>You need:</span>{" "}
                          {(recipe.missing_ingredients || []).join(", ") || "-"}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {clickable && <ArrowRight size={15} style={{ color: accentColor }} />}
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
