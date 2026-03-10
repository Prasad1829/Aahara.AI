import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, Salad, Check, Loader2, ChefHat, ArrowRight, Clock, Leaf, Flame } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const FALLBACK_IMAGE = "https://source.unsplash.com/200x200/?food";

function getRecipeImage(name = "") {
  const query = encodeURIComponent(String(name || "recipe"));
  return `https://source.unsplash.com/200x200/?food,${query}`;
}

const VEGETABLES = [
  { id: "tomato",      name: "Tomato",       emoji: "🍅", color: "#e05252" },
  { id: "potato",      name: "Potato",       emoji: "🥔", color: "#c8873a" },
  { id: "onion",       name: "Onion",        emoji: "🧅", color: "#a07cc5" },
  { id: "garlic",      name: "Garlic",       emoji: "🧄", color: "#c8a03a" },
  { id: "carrot",      name: "Carrot",       emoji: "🥕", color: "#e07a2a" },
  { id: "spinach",     name: "Spinach",      emoji: "🥬", color: "#4a9e6b" },
  { id: "broccoli",    name: "Broccoli",     emoji: "🥦", color: "#3d8c5a" },
  { id: "capsicum",    name: "Capsicum",     emoji: "🫑", color: "#6aaa5a" },
  { id: "cucumber",    name: "Cucumber",     emoji: "🥒", color: "#5aaa88" },
  { id: "corn",        name: "Corn",         emoji: "🌽", color: "#c8b03a" },
  { id: "mushroom",    name: "Mushroom",     emoji: "🍄", color: "#a07050" },
  { id: "eggplant",    name: "Eggplant",     emoji: "🍆", color: "#8a52c8" },
  { id: "peas",        name: "Green Peas",   emoji: "🫛", color: "#5aaa3a" },
  { id: "cauliflower", name: "Cauliflower",  emoji: "🥦", color: "#9aaa8a" },
  { id: "beans",       name: "Beans",        emoji: "🫘", color: "#a07050" },
  { id: "lemon",       name: "Lemon",        emoji: "🍋", color: "#c8c03a" },
  { id: "chilli",      name: "Green Chilli", emoji: "🌶️", color: "#e03a3a" },
  { id: "ginger",      name: "Ginger",       emoji: "🫚", color: "#c8873a" },
];

export default function SelectVegetablesPage() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const selectedIngredientNames = [...selected]
    .map((id) => VEGETABLES.find((v) => v.id === id)?.name)
    .filter(Boolean);

  const toggle = (id) => setSelected((prev) => {
    const next = new Set(prev);
    next.has(id) ? next.delete(id) : next.add(id);
    return next;
  });

  const handleSubmit = async () => {
    if (selected.size === 0) return;
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const ingredients = selectedIngredientNames;
      const res = await fetch(`${API_BASE}/recommend-recipes`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ ingredients }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to fetch recipes.");
      setResult(data);
    } catch (err) { setResult({ error: err.message || "Failed to fetch recipes." }); }
    finally { setLoading(false); }
  };

  const goToRecipe = (recipe) => {
    navigate(`/recipe/${encodeURIComponent(recipe.name)}`, {
      state: { recipe, detectedIngredients: selectedIngredientNames },
    });
  };

  const CARD = { background: "rgba(250,246,237,0.97)", borderRadius: 20, padding: 24, backdropFilter: "blur(8px)" };

  return (
      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "40px 24px 80px" }}>

          <motion.button initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }}
            onClick={() => navigate("/dashboard")}
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.82rem",
              color: "rgba(255,255,255,0.7)", background: "none", border: "none", cursor: "pointer", marginBottom: 24 }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "rgba(255,255,255,0.7)")}>
            <ArrowLeft size={15} /> Back to Dashboard
          </motion.button>

          {/* Veg Grid */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            style={{ ...CARD, marginBottom: 16 }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(100px, 1fr))", gap: 10 }}>
              {VEGETABLES.map((veg, i) => {
                const isSel = selected.has(veg.id);
                return (
                  <motion.div key={veg.id}
                    initial={{ opacity: 0, scale: 0.88 }} animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.02 }}
                    whileHover={{ scale: 1.06 }} whileTap={{ scale: 0.93 }}
                    onClick={() => toggle(veg.id)}
                    style={{ position: "relative", borderRadius: 14, padding: "14px 8px",
                      textAlign: "center", cursor: "pointer",
                      background: isSel ? `${veg.color}18` : "rgba(0,0,0,0.03)",
                      border: `2px solid ${isSel ? veg.color : "rgba(0,0,0,0.08)"}`,
                      boxShadow: isSel ? `0 0 14px ${veg.color}33` : "none",
                      transition: "all 0.2s" }}>
                    <AnimatePresence>
                      {isSel && (
                        <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }}
                          style={{ position: "absolute", top: 5, right: 5, width: 17, height: 17,
                            borderRadius: "50%", background: veg.color,
                            display: "flex", alignItems: "center", justifyContent: "center" }}>
                          <Check size={10} color="#fff" />
                        </motion.div>
                      )}
                    </AnimatePresence>
                    <div style={{ fontSize: "1.8rem", marginBottom: 5 }}>{veg.emoji}</div>
                    <p style={{ fontSize: "0.68rem", fontWeight: 600,
                      color: isSel ? veg.color : "#6b7280" }}>
                      {veg.name}
                    </p>
                  </motion.div>
                );
              })}
            </div>

            {/* Selected tags */}
            {selected.size > 0 && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                style={{ marginTop: 16, paddingTop: 16, borderTop: "1px solid rgba(0,0,0,0.08)",
                  display: "flex", flexWrap: "wrap", gap: 6 }}>
                {[...selected].map((id) => {
                  const veg = VEGETABLES.find((v) => v.id === id);
                  return (
                    <span key={id} style={{ padding: "5px 12px", borderRadius: 20,
                      fontSize: "0.76rem", fontWeight: 500,
                      background: `${veg.color}15`, color: veg.color, border: `1px solid ${veg.color}44` }}>
                      {veg.emoji} {veg.name}
                    </span>
                  );
                })}
              </motion.div>
            )}
          </motion.div>

          {/* Result */}
          {result && !result.error && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
              style={{ ...CARD, marginBottom: 16, border: "1px solid rgba(200,135,58,0.3)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <ChefHat size={18} color="#C8873A" />
                <span style={{ fontWeight: 700, color: "#C8873A" }}>Recipe Suggestions</span>
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
                <p style={{ fontSize: "0.85rem", color: "#4b5563", lineHeight: 1.7, whiteSpace: "pre-line" }}>
                  {result.message || "No recipes found for the selected ingredients."}
                </p>
              )}
            </motion.div>
          )}

          {result?.error && (
            <div style={{ marginBottom: 14, padding: "12px 16px", borderRadius: 12,
              background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)",
              color: "#dc2626", fontSize: "0.85rem" }}>
              {result.error}
            </div>
          )}

          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
            onClick={handleSubmit} disabled={selected.size === 0 || loading}
            style={{ width: "100%", padding: "15px", borderRadius: 16, border: "none",
              background: selected.size === 0 ? "rgba(0,0,0,0.12)" : "#C8873A",
              color: selected.size === 0 ? "#9ca3af" : "#fff",
              fontSize: "1rem", fontWeight: 700, fontFamily: "inherit",
              cursor: selected.size === 0 ? "not-allowed" : "pointer",
              display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
            {loading
              ? <><Loader2 size={18} style={{ animation: "spin 1s linear infinite" }} /> Getting Recipes...</>
              : <><ChefHat size={18} /> Find Recipes</>}
          </motion.button>
      </div>
  );
}
