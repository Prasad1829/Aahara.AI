import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, ArrowLeft, X, ImageIcon, Loader2, ChefHat, Plus, Clock, Leaf, Flame, ArrowRight } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const FALLBACK_IMAGE = "https://source.unsplash.com/200x200/?food";

function getRecipeImage(name = "") {
  const query = encodeURIComponent(String(name || "recipe"));
  return `https://source.unsplash.com/200x200/?food,${query}`;
}

export default function UploadImagePage() {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const addFiles = (newFiles) => {
    const images = Array.from(newFiles).filter((f) => f.type.startsWith("image/"));
    setFiles((prev) => [...prev, ...images.map((f) => ({ file: f, preview: URL.createObjectURL(f) }))]);
    setResults([]); setRecommendations([]); setError(null);
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
    setResults([]);
    setRecommendations([]);
  };

  const onDrop = useCallback((e) => { e.preventDefault(); setDragOver(false); addFiles(e.dataTransfer.files); }, []);

  const handleSubmit = async () => {
    if (files.length === 0) return;
    setLoading(true); setError(null); setResults([]);
    try {
      const token = localStorage.getItem("token");
      const allResults = [];
      for (const { file } of files) {
        const formData = new FormData();
        formData.append("file", file);
        const res = await fetch(`${API_BASE}/upload`, {
          method: "POST", headers: { Authorization: `Bearer ${token}` }, body: formData,
        });
        const data = await res.json();
        if (!res.ok) allResults.push({ error: data.detail || "Upload failed" });
        else allResults.push({ ingredients: data.detected_ingredients || [], recipes: data.recommended_recipes || [] });
      }
      setResults(allResults);

      const combinedIngredients = [
        ...new Set(allResults.flatMap((r) => r.detected_ingredients || [])),
      ];
      if (combinedIngredients.length > 0) {
        const res = await fetch(`${API_BASE}/recommend?ingredients=${encodeURIComponent(combinedIngredients.join(","))}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (res.ok) {
          setRecommendations(data.recommended_recipes || []);
        } else {
          setRecommendations([]);
        }
      } else {
        setRecommendations([]);
      }
    } catch (err) { setError("Network error: " + err.message); }
    finally { setLoading(false); }
  };

  const allIngredients = [...new Set(results.flatMap((r) => r.ingredients || []))];
  const allRecipes = recommendations.length
    ? recommendations
    : Object.values(
    results.flatMap((r) => r.recipes || []).reduce((acc, r) => { const k = r.name || r; if (!acc[k]) acc[k] = r; return acc; }, {})
  );

  const goToRecipe = (recipe) => {
    navigate(`/recipe/${encodeURIComponent(recipe.name || recipe)}`, {
      state: { recipe, detectedIngredients: allIngredients },
    });
  };

  const CARD = { background: "rgba(250,246,237,0.97)", borderRadius: 20, padding: 24, backdropFilter: "blur(8px)" };

  return (
      <div style={{ maxWidth: 760, margin: "0 auto", padding: "40px 24px 80px" }}>

          <motion.button initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }}
            onClick={() => navigate("/dashboard")}
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.82rem",
              color: "rgba(255,255,255,0.7)", background: "none", border: "none", cursor: "pointer", marginBottom: 24 }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "rgba(255,255,255,0.7)")}>
            <ArrowLeft size={15} /> Back to Dashboard
          </motion.button>

          {/* Drop zone */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            style={{ ...CARD, marginBottom: 16 }}>
            <div onDrop={onDrop}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onClick={() => document.getElementById("file-input").click()}
              style={{
                border: `2px dashed ${dragOver ? "#4a9e6b" : "rgba(74,158,107,0.35)"}`,
                borderRadius: 16, padding: files.length > 0 ? "18px" : "48px 24px",
                textAlign: "center", cursor: "pointer",
                background: dragOver ? "rgba(74,158,107,0.06)" : "rgba(74,158,107,0.02)",
                transition: "all 0.2s",
              }}>
              {files.length === 0 ? (
                <>
                  <ImageIcon size={40} style={{ color: "#4a9e6b", opacity: 0.5, marginBottom: 12 }} />
                  <p style={{ fontSize: "1rem", fontWeight: 600, color: "#2d2d2d", marginBottom: 4 }}>Drop images here</p>
                  <p style={{ fontSize: "0.82rem", color: "#9ca3af" }}>or click to browse — JPG, PNG, WEBP</p>
                </>
              ) : (
                <div style={{ display: "flex", alignItems: "center", gap: 8,
                  justifyContent: "center", color: "#4a9e6b", fontSize: "0.88rem", fontWeight: 600 }}>
                  <Plus size={16} /> Add more images
                </div>
              )}
              <input id="file-input" type="file" accept="image/*" multiple
                style={{ display: "none" }}
                onChange={(e) => {
                  addFiles(e.target.files);
                  e.target.value = "";
                }} />
            </div>

            {/* Previews */}
            <AnimatePresence>
              {files.length > 0 && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: 10, marginTop: 14 }}>
                  {files.map(({ preview, file }, idx) => (
                    <motion.div key={preview} initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
                      style={{ position: "relative", borderRadius: 12, overflow: "hidden",
                        border: "1px solid rgba(74,158,107,0.3)" }}>
                      <img src={preview} alt={file.name} style={{ width: "100%", height: 120, objectFit: "cover", display: "block" }} />
                      {results[idx] && !results[idx].error && (
                        <div style={{ position: "absolute", bottom: 0, left: 0, right: 0,
                          background: "rgba(74,158,107,0.85)", padding: "5px 8px" }}>
                          <p style={{ fontSize: "0.68rem", color: "#fff", fontWeight: 600 }}>
                            ✓ {(results[idx].ingredients || []).length} found
                          </p>
                        </div>
                      )}
                      {results[idx]?.error && (
                        <div style={{ position: "absolute", bottom: 0, left: 0, right: 0,
                          background: "rgba(239,68,68,0.85)", padding: "5px 8px" }}>
                          <p style={{ fontSize: "0.68rem", color: "#fff" }}>⚠ Error</p>
                        </div>
                      )}
                      <button onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                        style={{ position: "absolute", top: 6, right: 6, width: 24, height: 24,
                          borderRadius: "50%", background: "rgba(0,0,0,0.55)", border: "none",
                          color: "white", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <X size={12} />
                      </button>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {error && (
            <div style={{ marginBottom: 14, padding: "12px 16px", borderRadius: 12,
              background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)",
              color: "#dc2626", fontSize: "0.85rem" }}>
              {error}
            </div>
          )}

          {/* Detected Ingredients */}
          {allIngredients.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
              style={{ ...CARD, marginBottom: 16, border: "1px solid rgba(74,158,107,0.3)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <ChefHat size={18} color="#4a9e6b" />
                <span style={{ fontWeight: 700, color: "#4a9e6b" }}>Detected Ingredients ({allIngredients.length})</span>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {allIngredients.map((item, i) => (
                  <span key={i} style={{ padding: "6px 14px", borderRadius: 20, fontSize: "0.82rem", fontWeight: 500,
                    background: "rgba(74,158,107,0.12)", color: "#2d6a4a", border: "1px solid rgba(74,158,107,0.3)" }}>
                    {item}
                  </span>
                ))}
              </div>
            </motion.div>
          )}

          {/* Recipes */}
          {allRecipes.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
              style={{ ...CARD, border: "1px solid rgba(200,135,58,0.3)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                <ChefHat size={18} color="#C8873A" />
                <span style={{ fontWeight: 700, color: "#C8873A" }}>
                  Recommended Recipes ({allRecipes.length}) — tap to view
                </span>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {allRecipes.map((recipe, i) => (
                  <motion.div key={i}
                    initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
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
                          src={getRecipeImage(recipe.name || recipe)}
                          alt={recipe.name || recipe}
                          style={{ width: 56, height: 56, borderRadius: 12, objectFit: "cover", flexShrink: 0 }}
                          loading="lazy"
                          onError={(e) => {
                            e.currentTarget.onerror = null;
                            e.currentTarget.src = FALLBACK_IMAGE;
                          }}
                        />
                        <div style={{ flex: 1 }}>
                        <h3 style={{ fontWeight: 700, color: "#2d2d2d", fontSize: "0.95rem", marginBottom: 6 }}>
                          {recipe.name || recipe}
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
                        {recipe.missing_ingredients && recipe.missing_ingredients.length > 0 && (
                          <div style={{ marginTop: 8 }}>
                            <p style={{ fontSize: "0.72rem", fontWeight: 700, color: "#9ca3af",
                              textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>
                              Missing Ingredients
                            </p>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                              {recipe.missing_ingredients.map((item, idx) => (
                                <span key={`${item}-${idx}`} style={{ padding: "3px 10px", borderRadius: 20,
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
            </motion.div>
          )}

          {/* Submit */}
          {files.length > 0 && (
            <motion.button initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              onClick={handleSubmit} disabled={loading}
              whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
              style={{ marginTop: 16, width: "100%", padding: "15px", borderRadius: 16,
                border: "none", cursor: loading ? "not-allowed" : "pointer",
                background: loading ? "rgba(74,158,107,0.4)" : "#4a9e6b",
                color: "#fff", fontSize: "1rem", fontWeight: 700, fontFamily: "inherit",
                display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
              {loading
                ? <><Loader2 size={18} style={{ animation: "spin 1s linear infinite" }} /> Analyzing...</>
                : <><ChefHat size={18} /> Generate Recipe ({files.length} image{files.length > 1 ? "s" : ""})</>}
            </motion.button>
          )}
      </div>
  );
}
