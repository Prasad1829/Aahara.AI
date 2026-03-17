import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, Plus, X, Loader2, ChefHat, ArrowRight, Clock, Leaf, Flame } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const FALLBACK_IMAGE = "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80";

function getRecipeImage(name = "") {
  const recipes = {
    "chicken": "https://images.unsplash.com/photo-1598103442097-8b74394b95c2?w=400&q=80",
    "fish": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&q=80",
    "egg": "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=400&q=80",
    "rice": "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=400&q=80",
    "dal": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&q=80",
    "paneer": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400&q=80",
    "biryani": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&q=80",
    "curry": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&q=80",
    "roti": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80",
    "sambar": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80",
    "dosa": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=400&q=80",
    "idli": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=400&q=80",
    "soup": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&q=80",
    "salad": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&q=80",
    "vegetable": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&q=80",
    "potato": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400&q=80",
    "tomato": "https://images.unsplash.com/photo-1558818498-28c1e002b655?w=400&q=80",
    "mushroom": "https://images.unsplash.com/photo-1504545102780-26774c1bb073?w=400&q=80",
    "spinach": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400&q=80",
    "eggplant": "https://images.unsplash.com/photo-1613743990305-99b1c1945b80?w=400&q=80",
    "baingan": "https://images.unsplash.com/photo-1613743990305-99b1c1945b80?w=400&q=80",
    "bharta": "https://images.unsplash.com/photo-1613743990305-99b1c1945b80?w=400&q=80",
    "pulao": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&q=80",
    "sabzi": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&q=80",
    "masala": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&q=80",
    "noodles": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&q=80",
    "pasta": "https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=400&q=80",
  };

  const nameLower = (name || "").toLowerCase();
  for (const [key, url] of Object.entries(recipes)) {
    if (nameLower.includes(key)) return url;
  }
  return FALLBACK_IMAGE;
}

export default function ManualEntryPage() {
  const navigate = useNavigate();
  const [input, setInput] = useState("");
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [recipes, setRecipes] = useState([]);
  const [error, setError] = useState(null);

  const addIngredient = () => {
    const trimmed = input.trim();
    if (!trimmed) return;
    const newItems = trimmed.split(",").map((s) => s.trim()).filter(Boolean);
    setIngredients((prev) => [...new Set([...prev, ...newItems])]);
    setInput("");
    setRecipes([]); setError(null);
  };

  const removeIngredient = (item) => {
    setIngredients((prev) => prev.filter((x) => x !== item));
    setRecipes([]); setError(null);
  };

  const handleFind = async () => {
    if (ingredients.length === 0) return;
    setLoading(true); setError(null); setRecipes([]);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(
        `${API_BASE}/recommend?ingredients=${encodeURIComponent(ingredients.join(","))}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to fetch recipes");
      setRecipes(data.recommended_recipes || []);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  const goToRecipe = (recipe) => {
    navigate(`/recipe/${encodeURIComponent(recipe.name || recipe)}`, {
      state: { recipe, detectedIngredients: ingredients },
    });
  };

  const CARD = { background: "rgba(250,246,237,0.97)", borderRadius: 20, padding: 20, backdropFilter: "blur(8px)" };

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "24px 24px 80px" }}>
      <motion.button initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }}
        onClick={() => navigate("/dashboard")}
        style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.82rem",
          color: "#ffffff", background: "rgba(255,255,255,0.15)", border: "1px solid rgba(255,255,255,0.3)",
          borderRadius: 8, padding: "6px 12px", cursor: "pointer", marginBottom: 20 }}
        onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.25)")}
        onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.15)")}>
        <ArrowLeft size={15} /> Back to Dashboard
      </motion.button>

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
        style={{ ...CARD, marginBottom: 14, border: "1px solid rgba(74,158,107,0.2)" }}>
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
            style={{ flex: 1, padding: "10px 14px", borderRadius: 10,
              background: "#fdfaf5", border: "1.5px solid rgba(74,158,107,0.3)",
              color: "#2d2d2d", fontSize: "0.88rem", outline: "none", fontFamily: "inherit" }}
            onFocus={(e) => {
              e.target.style.border = "1.5px solid #4a9e6b";
              e.target.style.boxShadow = "0 0 0 3px rgba(74,158,107,0.1)";
            }}
            onBlur={(e) => {
              e.target.style.border = "1.5px solid rgba(74,158,107,0.3)";
              e.target.style.boxShadow = "none";
            }}
          />
          <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
            onClick={addIngredient}
            style={{ padding: "10px 16px", borderRadius: 10, border: "none",
              background: "#4a9e6b", color: "#fff", cursor: "pointer", fontFamily: "inherit",
              display: "flex", alignItems: "center", gap: 6, fontWeight: 700, fontSize: "0.88rem" }}>
            <Plus size={16} /> Add
          </motion.button>
        </div>

        <AnimatePresence>
          {ingredients.length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
              {ingredients.map((item) => (
                <motion.span key={item}
                  initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  style={{ display: "flex", alignItems: "center", gap: 5,
                    padding: "5px 12px", borderRadius: 20, fontSize: "0.8rem", fontWeight: 600,
                    background: "rgba(74,158,107,0.12)", color: "#2d6a4a",
                    border: "1px solid rgba(74,158,107,0.3)" }}>
                  {item}
                  <button onClick={() => removeIngredient(item)}
                    style={{ background: "none", border: "none", cursor: "pointer",
                      padding: 0, display: "flex", alignItems: "center", color: "#2d6a4a" }}>
                    <X size={12} />
                  </button>
                </motion.span>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {error && (
        <div style={{ marginBottom: 12, padding: "10px 14px", borderRadius: 10,
          background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)",
          color: "#dc2626", fontSize: "0.85rem" }}>
          {error}
        </div>
      )}

      {recipes.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
          style={{ ...CARD, border: "1px solid rgba(200,135,58,0.3)", marginBottom: 14 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
            <ChefHat size={16} color="#C8873A" />
            <span style={{ fontWeight: 700, color: "#C8873A", fontSize: "0.9rem" }}>
              Recipes Found ({recipes.length}) — tap to view
            </span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {recipes.map((recipe, i) => (
              <motion.div key={i}
                initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                whileHover={{ x: 4 }} whileTap={{ scale: 0.99 }}
                onClick={() => goToRecipe(recipe)}
                style={{ padding: "12px 14px", borderRadius: 12, cursor: "pointer",
                  background: "rgba(200,135,58,0.06)", border: "1px solid rgba(200,135,58,0.2)",
                  transition: "all 0.2s" }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "rgba(200,135,58,0.12)";
                  e.currentTarget.style.border = "1px solid rgba(200,135,58,0.45)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "rgba(200,135,58,0.06)";
                  e.currentTarget.style.border = "1px solid rgba(200,135,58,0.2)";
                }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1 }}>
                    <img
                      src={getRecipeImage(recipe.name || recipe)}
                      alt={recipe.name || recipe}
                      style={{ width: 48, height: 48, borderRadius: 10, objectFit: "cover", flexShrink: 0 }}
                      loading="lazy"
                      onError={(e) => { e.currentTarget.onerror = null; e.currentTarget.src = FALLBACK_IMAGE; }}
                    />
                    <div style={{ flex: 1 }}>
                      <h3 style={{ fontWeight: 700, color: "#2d2d2d", fontSize: "0.88rem", marginBottom: 5 }}>
                        {recipe.name || recipe}
                      </h3>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                        {recipe.is_veg !== undefined && (
                          <span style={{ display: "flex", alignItems: "center", gap: 4,
                            padding: "2px 8px", borderRadius: 20, fontSize: "0.68rem", fontWeight: 600,
                            background: recipe.is_veg ? "rgba(74,158,107,0.12)" : "rgba(239,68,68,0.1)",
                            color: recipe.is_veg ? "#2d6a4a" : "#dc2626",
                            border: `1px solid ${recipe.is_veg ? "rgba(74,158,107,0.3)" : "rgba(239,68,68,0.25)"}` }}>
                            {recipe.is_veg ? <Leaf size={10} /> : <Flame size={10} />}
                            {recipe.is_veg ? "Veg" : "Non-Veg"}
                          </span>
                        )}
                        {recipe.cooking_time_minutes && (
                          <span style={{ display: "flex", alignItems: "center", gap: 4,
                            padding: "2px 8px", borderRadius: 20, fontSize: "0.68rem", fontWeight: 600,
                            background: "rgba(200,135,58,0.1)", color: "#C8873A",
                            border: "1px solid rgba(200,135,58,0.25)" }}>
                            <Clock size={10} /> {recipe.cooking_time_minutes} min
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <ArrowRight size={15} style={{ color: "#C8873A" }} />
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {ingredients.length > 0 && (
        <motion.button initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          onClick={handleFind} disabled={loading}
          whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
          style={{ marginTop: 4, width: "100%", padding: "13px", borderRadius: 14,
            border: "none", cursor: loading ? "not-allowed" : "pointer",
            background: loading ? "rgba(74,158,107,0.4)" : "#4a9e6b",
            color: "#fff", fontSize: "0.95rem", fontWeight: 700, fontFamily: "inherit",
            display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
          {loading
            ? <><Loader2 size={16} style={{ animation: "spin 1s linear infinite" }} /> Finding Recipes...</>
            : <><ChefHat size={16} /> Find Recipes ({ingredients.length} ingredient{ingredients.length > 1 ? "s" : ""})</>}
        </motion.button>
      )}
    </div>
  );
}
