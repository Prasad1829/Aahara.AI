import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, Plus, X, Loader2, ChefHat, ArrowRight } from "lucide-react";
import RecipeGenerationLoader from "../components/RecipeGenerationLoader";
import RecipeRecommendationSection from "../components/RecipeRecommendationSection";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function ManualEntryPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const restoredState = location.state?.restoreState;
  const [input, setInput] = useState(restoredState?.input || "");
  const [ingredients, setIngredients] = useState(restoredState?.ingredients || []);
  const [loading, setLoading] = useState(false);
  const [recommendedRecipes, setRecommendedRecipes] = useState(restoredState?.recommendedRecipes || []);
  const [additionalRecipes, setAdditionalRecipes] = useState(restoredState?.additionalRecipes || []);
  const [error, setError] = useState(restoredState?.error || null);

  const addIngredient = () => {
    const trimmed = input.trim();
    if (!trimmed) return;
    const newItems = trimmed.split(",").map((s) => s.trim()).filter(Boolean);
    setIngredients((prev) => [...new Set([...prev, ...newItems])]);
    setInput("");
    setRecommendedRecipes([]);
    setAdditionalRecipes([]);
    setError(null);
  };

  const removeIngredient = (item) => {
    setIngredients((prev) => prev.filter((x) => x !== item));
    setRecommendedRecipes([]);
    setAdditionalRecipes([]);
    setError(null);
  };

  const handleFind = async () => {
    if (ingredients.length === 0) return;
    setLoading(true);
    setError(null);
    setRecommendedRecipes([]);
    setAdditionalRecipes([]);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(
        `${API_BASE}/recommend?ingredients=${encodeURIComponent(ingredients.join(","))}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to fetch recipes");
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
        detectedIngredients: ingredients,
        returnTo: {
          path: "/manual-entry",
          state: {
            input,
            ingredients,
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
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "24px 24px 80px" }}>
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
            Type Your Ingredients
          </h2>
        </div>

        <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addIngredient()}
            placeholder="e.g. chicken, onion, tomato (comma separated)"
            style={{
              flex: 1,
              padding: "10px 14px",
              borderRadius: 10,
              background: "#fdfaf5",
              border: "1.5px solid rgba(74,158,107,0.3)",
              color: "#2d2d2d",
              fontSize: "0.88rem",
              outline: "none",
              fontFamily: "inherit",
            }}
            onFocus={(e) => {
              e.target.style.border = "1.5px solid #4a9e6b";
              e.target.style.boxShadow = "0 0 0 3px rgba(74,158,107,0.1)";
            }}
            onBlur={(e) => {
              e.target.style.border = "1.5px solid rgba(74,158,107,0.3)";
              e.target.style.boxShadow = "none";
            }}
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={addIngredient}
            style={{
              padding: "10px 16px",
              borderRadius: 10,
              border: "none",
              background: "#4a9e6b",
              color: "#fff",
              cursor: "pointer",
              fontFamily: "inherit",
              display: "flex",
              alignItems: "center",
              gap: 6,
              fontWeight: 700,
              fontSize: "0.88rem",
            }}
          >
            <Plus size={16} /> Add
          </motion.button>
        </div>

        <AnimatePresence>
          {ingredients.length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
              {ingredients.map((item) => (
                <motion.span
                  key={item}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 5,
                    padding: "5px 12px",
                    borderRadius: 20,
                    fontSize: "0.8rem",
                    fontWeight: 600,
                    background: "rgba(74,158,107,0.12)",
                    color: "#2d6a4a",
                    border: "1px solid rgba(74,158,107,0.3)",
                  }}
                >
                  {item}
                  <button
                    onClick={() => removeIngredient(item)}
                    style={{ background: "none", border: "none", cursor: "pointer", padding: 0, display: "flex", alignItems: "center", color: "#2d6a4a" }}
                  >
                    <X size={12} />
                  </button>
                </motion.span>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
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
          title="Finding recipes from your ingredients"
          description="We're matching your ingredient list against the recipe database and sorting the best fits."
          steps={[
            { label: "Checking ingredients", Icon: ChefHat },
            { label: "Finding close matches", Icon: ArrowRight },
            { label: "Preparing suggestions", Icon: Plus },
          ]}
        />
      )}

      <RecipeRecommendationSection
        title="Recommended Recipes"
        recipes={recommendedRecipes}
        ingredientsFallback={ingredients}
        onRecipeClick={goToRecipe}
        cardStyle={CARD}
      />

      <RecipeRecommendationSection
        title="You can try these recipes by adding other ingredients"
        recipes={additionalRecipes}
        ingredientsFallback={ingredients}
        onRecipeClick={goToRecipe}
        variant="additional"
        cardStyle={CARD}
      />

      {ingredients.length > 0 && (
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
            : <><ChefHat size={16} /> Find Recipes ({ingredients.length} ingredient{ingredients.length > 1 ? "s" : ""})</>}
        </motion.button>
      )}
    </div>
  );
}
