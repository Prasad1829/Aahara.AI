import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, PenLine, Plus, X, ChefHat, Loader2, ArrowRight, Clock, Leaf, Flame } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const FALLBACK_IMAGE = "https://source.unsplash.com/200x200/?food";

function getRecipeImage(name = "") {
  const query = encodeURIComponent(String(name || "recipe"));
  return `https://source.unsplash.com/200x200/?food,${query}`;
}

export default function ManualEntryPage() {
  const navigate = useNavigate();
  const [input, setInput] = useState("");
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const addIngredient = () => {
    const val = input.trim();
    if (!val || ingredients.includes(val)) return;
    setIngredients((prev) => [...prev, val]);
    setInput("");
  };

  const handleSubmit = async () => {
    if (ingredients.length === 0) return;
    setLoading(true); setError(null); setResult(null);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_BASE}/recommend-recipes`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ ingredients }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed");
      setResult(data);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  const goToRecipe = (recipe) => {
    navigate(`/recipe/${encodeURIComponent(recipe.name)}`, {
      state: { recipe, detectedIngredients: ingredients },
    });
  };

  const CARD = { background: "rgba(250,246,237,0.97)", borderRadius: 20, padding: 24, backdropFilter: "blur(8px)" };

  return (
      <div style={{ maxWidth: 660, margin: "0 auto", padding: "40px 24px 80px" }}>

          <motion.button initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }}
            onClick={() => navigate("/dashboard")}
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.82rem",
              color: "rgba(255,255,255,0.7)", background: "none", border: "none", cursor: "pointer", marginBottom: 24 }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "rgba(255,255,255,0.7)")}>
            <ArrowLeft size={15} /> Back to Dashboard
          </motion.button>

          {/* Input */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            style={{ ...CARD, marginBottom: 16 }}>
            <div style={{ display: "flex", gap: 10 }}>
              <input type="text" value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && addIngredient()}
                placeholder="e.g. Tomato, Onion, Garlic..."
                style={{ flex: 1, borderRadius: 12, padding: "12px 16px",
                  fontSize: "0.9rem", color: "#2d2d2d", outline: "none",
                  background: "#fff", border: "1.5px solid rgba(200,135,58,0.3)",
                  fontFamily: "inherit" }}
                onFocus={(e) => {
                  e.target.style.border = "1.5px solid #C8873A";
                  e.target.style.boxShadow = "0 0 0 3px rgba(200,135,58,0.1)";
                }}
                onBlur={(e) => {
                  e.target.style.border = "1.5px solid rgba(200,135,58,0.3)";
                  e.target.style.boxShadow = "none";
                }} />
              <motion.button whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
                onClick={addIngredient}
                style={{ display: "flex", alignItems: "center", gap: 7,
                  padding: "12px 20px", borderRadius: 12, border: "none",
                  background: "#C8873A", color: "#fff",
                  fontSize: "0.9rem", fontWeight: 700, cursor: "pointer", fontFamily: "inherit" }}>
                <Plus size={17} /> Add
              </motion.button>
            </div>

            {/* Tags */}
            <AnimatePresence>
              {ingredients.length > 0 && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  style={{ marginTop: 16, paddingTop: 16, borderTop: "1px solid rgba(0,0,0,0.08)" }}>
                  <p style={{ fontSize: "0.7rem", fontWeight: 700, textTransform: "uppercase",
                    letterSpacing: "0.1em", color: "#9ca3af", marginBottom: 10 }}>
                    Your Ingredients ({ingredients.length})
                  </p>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                    <AnimatePresence>
                      {ingredients.map((item) => (
                        <motion.span key={item}
                          initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.8 }}
                          style={{ display: "flex", alignItems: "center", gap: 7,
                            padding: "7px 14px", borderRadius: 20, fontSize: "0.82rem", fontWeight: 500,
                            background: "rgba(200,135,58,0.1)", color: "#7c4a10",
                            border: "1px solid rgba(200,135,58,0.3)" }}>
                          {item}
                          <button onClick={() => setIngredients((p) => p.filter((i) => i !== item))}
                            style={{ background: "none", border: "none", color: "#C8873A",
                              cursor: "pointer", padding: 0, display: "flex", alignItems: "center" }}>
                            <X size={12} />
                          </button>
                        </motion.span>
                      ))}
                    </AnimatePresence>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {error && (
            <div style={{ marginBottom: 14, padding: "12px 16px", borderRadius: 12,
              background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)",
              color: "#dc2626", fontSize: "0.85rem" }}>
              {error}
            </div>
          )}

          {result && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
              style={{ ...CARD, marginBottom: 16, border: "1px solid rgba(74,158,107,0.3)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                <ChefHat size={18} color="#4a9e6b" />
                <span style={{ fontWeight: 700, color: "#4a9e6b" }}>Recipe Suggestions</span>
              </div>
              {Array.isArray(result.recipes) && result.recipes.length === 0 && (
                <p style={{ fontSize: "0.85rem", color: "#4b5563", lineHeight: 1.7 }}>
                  {result.message || "No recipes found for the selected ingredients."}
                </p>
              )}
              {Array.isArray(result.recipes) && result.recipes.length > 0 && (
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {result.recipes.map((recipe, idx) => (
                    <motion.div key={`${recipe.name}-${idx}`}
                      initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      whileHover={{ x: 4 }} whileTap={{ scale: 0.99 }}
                      onClick={() => goToRecipe(recipe)}
                      style={{ padding: "14px 16px", borderRadius: 14, cursor: "pointer",
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
                        <div style={{ display: "flex", alignItems: "center", gap: 12, flex: 1 }}>
                          <img
                            src={getRecipeImage(recipe.name)}
                            alt={recipe.name}
                            style={{ width: 56, height: 56, borderRadius: 12, objectFit: "cover", flexShrink: 0 }}
                            loading="lazy"
                            onError={(e) => {
                              e.currentTarget.onerror = null;
                              e.currentTarget.src = FALLBACK_IMAGE;
                            }}
                          />
                          <div style={{ flex: 1 }}>
                            <h3 style={{ fontWeight: 700, color: "#2d2d2d", fontSize: "0.95rem", marginBottom: 6 }}>
                              {recipe.name}
                            </h3>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                              {recipe.is_veg !== undefined && (
                                <span style={{ display: "flex", alignItems: "center", gap: 4,
                                  padding: "3px 10px", borderRadius: 20, fontSize: "0.72rem", fontWeight: 600,
                                  background: recipe.is_veg ? "rgba(74,158,107,0.12)" : "rgba(239,68,68,0.1)",
                                  color: recipe.is_veg ? "#2d6a4a" : "#dc2626",
                                  border: `1px solid ${recipe.is_veg ? "rgba(74,158,107,0.3)" : "rgba(239,68,68,0.25)"}` }}>
                                  {recipe.is_veg ? <Leaf size={11} /> : <Flame size={11} />}
                                  {recipe.is_veg ? "Veg" : "Non-Veg"}
                                </span>
                              )}
                              {recipe.cooking_time_minutes && (
                                <span style={{ display: "flex", alignItems: "center", gap: 4,
                                  padding: "3px 10px", borderRadius: 20, fontSize: "0.72rem", fontWeight: 600,
                                  background: "rgba(200,135,58,0.1)", color: "#C8873A",
                                  border: "1px solid rgba(200,135,58,0.25)" }}>
                                  <Clock size={11} /> {recipe.cooking_time_minutes} min
                                </span>
                              )}
                            </div>
                            {recipe.missing_ingredients?.length > 0 && (
                              <div style={{ marginTop: 8 }}>
                                <p style={{ fontSize: "0.72rem", fontWeight: 700, color: "#9ca3af",
                                  textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>
                                  Missing Ingredients
                                </p>
                                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                                  {recipe.missing_ingredients.map((item, mIdx) => (
                                    <span key={`${item}-${mIdx}`} style={{ padding: "3px 10px", borderRadius: 20,
                                      fontSize: "0.72rem", fontWeight: 600,
                                      background: "rgba(239,68,68,0.08)", color: "#dc2626",
                                      border: "1px solid rgba(239,68,68,0.2)" }}>
                                      {item}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                        <ArrowRight size={17} style={{ color: "#C8873A", marginLeft: 10 }} />
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
              {!Array.isArray(result.recipes) && (
                <p style={{ fontSize: "0.85rem", color: "#4b5563", whiteSpace: "pre-line", lineHeight: 1.7 }}>
                  {result.message || "No recipes found for the selected ingredients."}
                </p>
              )}
            </motion.div>
          )}

          <motion.button whileHover={ingredients.length > 0 ? { scale: 1.02 } : {}}
            whileTap={ingredients.length > 0 ? { scale: 0.97 } : {}}
            onClick={handleSubmit} disabled={ingredients.length === 0 || loading}
            style={{ width: "100%", padding: "15px", borderRadius: 16, border: "none",
              background: ingredients.length === 0 ? "rgba(0,0,0,0.12)" : "#4a9e6b",
              color: ingredients.length === 0 ? "#9ca3af" : "#fff",
              fontSize: "1rem", fontWeight: 700, fontFamily: "inherit",
              cursor: ingredients.length === 0 ? "not-allowed" : "pointer",
              display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
            {loading
              ? <><Loader2 size={18} style={{ animation: "spin 1s linear infinite" }} /> Getting Recipes...</>
              : <><ChefHat size={18} /> Find Recipes ({ingredients.length})</>}
          </motion.button>
      </div>
  );
}
