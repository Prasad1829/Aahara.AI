import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Check, Loader2, ChefHat, ArrowRight } from "lucide-react";
import RecipeGenerationLoader from "../components/RecipeGenerationLoader";
import RecipeRecommendationSection from "../components/RecipeRecommendationSection";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const INGREDIENT_SECTIONS = [
  {
    id: "veg",
    title: "Veg Ingredients",
    accent: "#4a9e6b",
    background: "rgba(74,158,107,0.08)",
    ingredients: [
      { id: "onion", name: "Onion", icon: "🧅", color: "#a07cc5" },
      { id: "tomato", name: "Tomato", icon: "🍅", color: "#e05252" },
      { id: "potato", name: "Potato", icon: "🥔", color: "#c8873a" },
      { id: "carrot", name: "Carrot", icon: "🥕", color: "#e07a2a" },
      { id: "cabbage", name: "Cabbage", icon: "🥬", color: "#6aa56a" },
      { id: "cauliflower", name: "Cauliflower", icon: "🥦", color: "#9aaa8a" },
      { id: "spinach", name: "Spinach", icon: "🥬", color: "#3d8c5a" },
      { id: "paneer", name: "Paneer", icon: "🧀", color: "#f0d98a" },
    ],
  },
  {
    id: "non-veg",
    title: "Non-Veg Ingredients",
    accent: "#c76a3a",
    background: "rgba(199,106,58,0.08)",
    ingredients: [
      { id: "chicken", name: "Chicken", icon: "🐔", color: "#d47b3d" },
      { id: "mutton", name: "Mutton", icon: "🍖", color: "#a55f4a" },
      { id: "fish", name: "Fish", icon: "🐟", color: "#4d88c7" },
      { id: "eggs", name: "Eggs", icon: "🥚", color: "#d4b15a" },
    ],
  },
];

const ALL_INGREDIENTS = INGREDIENT_SECTIONS.flatMap((section) => section.ingredients);

export default function SelectVegetablesPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const restoredState = location.state?.restoreState;
  const [selected, setSelected] = useState(restoredState?.selected || []);
  const [loading, setLoading] = useState(false);
  const [recommendedRecipes, setRecommendedRecipes] = useState(restoredState?.recommendedRecipes || []);
  const [additionalRecipes, setAdditionalRecipes] = useState(restoredState?.additionalRecipes || []);
  const [error, setError] = useState(restoredState?.error || null);

  const selectedNames = ALL_INGREDIENTS.filter((ingredient) => selected.includes(ingredient.id)).map((ingredient) => ingredient.name);

  const toggle = (id) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
    setRecommendedRecipes([]);
    setAdditionalRecipes([]);
    setError(null);
  };

  const handleFind = async () => {
    if (selected.length === 0) return;

    setLoading(true);
    setError(null);
    setRecommendedRecipes([]);
    setAdditionalRecipes([]);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch(
        `${API_BASE}/recommend?ingredients=${encodeURIComponent(selectedNames.join(","))}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const data = await res.json();

      if (res.status === 401) {
        localStorage.removeItem("token");
        navigate("/auth", { replace: true });
        return;
      }

      if (!res.ok) {
        throw new Error(data.detail || "Failed to fetch recipes");
      }

      setRecommendedRecipes(data.recommended_recipes || []);
      setAdditionalRecipes(data.additional_recipes || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const goToRecipe = (recipe) => {
    navigate(`/recipe/${encodeURIComponent(recipe.name || recipe)}`, {
      state: {
        recipe,
        detectedIngredients: selectedNames,
        returnTo: {
          path: "/select-vegetables",
          state: {
            selected,
            recommendedRecipes,
            additionalRecipes,
            error,
          },
        },
      },
    });
  };

  const CARD = { background: "rgba(250,246,237,0.97)", borderRadius: 20, padding: 20, backdropFilter: "blur(8px)" };

  return (
    <div style={{ maxWidth: 1180, margin: "0 auto", padding: "24px 20px 80px" }}>
      <motion.button
        initial={{ opacity: 0, x: -12 }}
        animate={{ opacity: 1, x: 0 }}
        onClick={() => navigate("/dashboard")}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          fontSize: "0.82rem",
          color: "#ffffff",
          background: "rgba(255,255,255,0.15)",
          border: "1px solid rgba(255,255,255,0.3)",
          borderRadius: 8,
          padding: "6px 12px",
          cursor: "pointer",
          marginBottom: 20,
        }}
        onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.25)")}
        onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.15)")}
      >
        <ArrowLeft size={15} /> Back to Dashboard
      </motion.button>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ ...CARD, marginBottom: 14, border: "1px solid rgba(74,158,107,0.2)" }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
          <ChefHat size={18} color="#4a9e6b" />
          <h2 style={{ fontWeight: 800, color: "#2d2d2d", fontSize: "1rem", margin: 0 }}>
            Select Your Ingredients
          </h2>
          {selected.length > 0 && (
            <span
              style={{
                marginLeft: "auto",
                padding: "3px 10px",
                borderRadius: 20,
                background: "rgba(74,158,107,0.15)",
                color: "#2d6a4a",
                fontSize: "0.75rem",
                fontWeight: 700,
              }}
            >
              {selected.length} selected
            </span>
          )}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {INGREDIENT_SECTIONS.map((section) => (
            <div
              key={section.id}
              style={{
                borderRadius: 16,
                border: `1px solid ${section.background.replace("0.08", "0.18")}`,
                background: "rgba(255,255,255,0.55)",
                padding: 12,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, marginBottom: 12 }}>
                <h3 style={{ margin: 0, fontSize: "0.92rem", fontWeight: 800, color: "#2d2d2d" }}>
                  {section.title}
                </h3>
                <span
                  style={{
                    padding: "4px 10px",
                    borderRadius: 999,
                    background: section.background,
                    color: section.accent,
                    fontSize: "0.72rem",
                    fontWeight: 700,
                  }}
                >
                  {section.ingredients.length} items
                </span>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(8, minmax(0, 1fr))", gap: 8 }}>
                {section.ingredients.map((ingredient) => {
                  const isSelected = selected.includes(ingredient.id);

                  return (
                    <motion.button
                      key={ingredient.id}
                      whileHover={{ scale: 1.03 }}
                      whileTap={{ scale: 0.97 }}
                      onClick={() => toggle(ingredient.id)}
                      style={{
                        minHeight: 74,
                        padding: "10px 6px",
                        borderRadius: 12,
                        border: "none",
                        cursor: "pointer",
                        fontFamily: "inherit",
                        transition: "all 0.2s",
                        position: "relative",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: 6,
                        background: isSelected ? `${ingredient.color}22` : "rgba(0,0,0,0.03)",
                        outline: isSelected ? `2px solid ${ingredient.color}` : "1px solid rgba(148,163,184,0.12)",
                        boxShadow: isSelected ? `0 10px 22px ${ingredient.color}20` : "none",
                      }}
                    >
                      {isSelected && (
                        <div
                          style={{
                            position: "absolute",
                            top: 6,
                            right: 6,
                            width: 16,
                            height: 16,
                            borderRadius: "50%",
                            background: ingredient.color,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          <Check size={11} color="#fff" strokeWidth={3} />
                        </div>
                      )}

                      <span
                        aria-hidden="true"
                        style={{
                          width: 32,
                          height: 32,
                          borderRadius: 10,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: "1.1rem",
                          background: isSelected ? `${ingredient.color}18` : "rgba(255,255,255,0.8)",
                        }}
                      >
                        {ingredient.icon}
                      </span>

                      <span
                        style={{
                          fontSize: "0.7rem",
                          fontWeight: 700,
                          color: isSelected ? ingredient.color : "#4b5563",
                          lineHeight: 1.15,
                          textAlign: "center",
                        }}
                      >
                        {ingredient.name}
                      </span>
                    </motion.button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {error && (
        <div
          style={{
            marginBottom: 12,
            padding: "10px 14px",
            borderRadius: 10,
            background: "rgba(239,68,68,0.1)",
            border: "1px solid rgba(239,68,68,0.25)",
            color: "#dc2626",
            fontSize: "0.85rem",
          }}
        >
          {error}
        </div>
      )}

      {loading && (
        <RecipeGenerationLoader
          title="Building recipe ideas"
          description="We're turning your selected ingredients into recipe matches with the best fit first."
          steps={[
            { label: "Reading selections", Icon: Check },
            { label: "Matching recipes", Icon: ChefHat },
            { label: "Finalizing results", Icon: ArrowRight },
          ]}
        />
      )}

      <RecipeRecommendationSection
        title="Recommended Recipes"
        recipes={recommendedRecipes}
        ingredientsFallback={selectedNames}
        onRecipeClick={goToRecipe}
        cardStyle={CARD}
      />

      <RecipeRecommendationSection
        title="You can try these recipes by adding other ingredients"
        recipes={additionalRecipes}
        ingredientsFallback={selectedNames}
        onRecipeClick={goToRecipe}
        variant="additional"
        cardStyle={CARD}
      />

      {selected.length > 0 && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={handleFind}
          disabled={loading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          style={{
            marginTop: 4,
            width: "100%",
            padding: "13px",
            borderRadius: 14,
            border: "none",
            cursor: loading ? "not-allowed" : "pointer",
            background: loading ? "rgba(74,158,107,0.4)" : "#4a9e6b",
            color: "#fff",
            fontSize: "0.95rem",
            fontWeight: 700,
            fontFamily: "inherit",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 10,
          }}
        >
          {loading
            ? <><Loader2 size={16} style={{ animation: "spin 1s linear infinite" }} /> Finding Recipes...</>
            : <><ChefHat size={16} /> Find Recipes ({selected.length} ingredient{selected.length > 1 ? "s" : ""})</>}
        </motion.button>
      )}
    </div>
  );
}
