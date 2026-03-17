import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, X, ImageIcon, Loader2, ChefHat, Plus, Clock, Leaf, Flame, ArrowRight } from "lucide-react";
import RecipeImage from "../components/RecipeImage";
import RecipeGenerationLoader from "../components/RecipeGenerationLoader";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

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

      const combinedIngredients = [...new Set(allResults.flatMap((r) => r.ingredients || []))];
      if (combinedIngredients.length > 0) {
        const res = await fetch(`${API_BASE}/recommend?ingredients=${encodeURIComponent(combinedIngredients.join(","))}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (res.ok) setRecommendations(data.recommended_recipes || []);
        else setRecommendations([]);
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
        results.flatMap((r) => r.recipes || []).reduce((acc, r) => {
          const k = r.name || r; if (!acc[k]) acc[k] = r; return acc;
        }, {})
      );

  const goToRecipe = (recipe) => {
    navigate(`/recipe/${encodeURIComponent(recipe.name || recipe)}`, {
      state: { recipe, detectedIngredients: allIngredients },
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

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
        style={{ ...CARD, marginBottom: 14 }}>
        <div onDrop={onDrop}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onClick={() => document.getElementById("file-input").click()}
          style={{
            border: `2px dashed ${dragOver ? "#4a9e6b" : "rgba(74,158,107,0.35)"}`,
            borderRadius: 14, padding: files.length > 0 ? "14px" : "40px 24px",
            textAlign: "center", cursor: "pointer",
            background: dragOver ? "rgba(74,158,107,0.06)" : "rgba(74,158,107,0.02)",
            transition: "all 0.2s",
          }}>
          {files.length === 0 ? (
            <>
              <ImageIcon size={34} style={{ color: "#4a9e6b", opacity: 0.5, marginBottom: 10 }} />
              <p style={{ fontSize: "0.95rem", fontWeight: 600, color: "#2d2d2d", marginBottom: 4 }}>Drop images here</p>
              <p style={{ fontSize: "0.78rem", color: "#9ca3af" }}>or click to browse — JPG, PNG, WEBP</p>
            </>
          ) : (
            <div style={{ display: "flex", alignItems: "center", gap: 8,
              justifyContent: "center", color: "#4a9e6b", fontSize: "0.88rem", fontWeight: 600 }}>
              <Plus size={16} /> Add more images
            </div>
          )}
          <input id="file-input" type="file" accept="image/*" multiple
            style={{ display: "none" }}
            onChange={(e) => { addFiles(e.target.files); e.target.value = ""; }} />
        </div>

        <AnimatePresence>
          {files.length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))", gap: 10, marginTop: 12 }}>
              {files.map(({ preview, file }, idx) => (
                <motion.div key={preview} initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
                  style={{ position: "relative", borderRadius: 10, overflow: "hidden",
                    border: "1px solid rgba(74,158,107,0.3)" }}>
                  <img src={preview} alt={file.name} style={{ width: "100%", height: 100, objectFit: "cover", display: "block" }} />
                  {results[idx] && !results[idx].error && (
                    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0,
                      background: "rgba(74,158,107,0.85)", padding: "4px 8px" }}>
                      <p style={{ fontSize: "0.68rem", color: "#fff", fontWeight: 600 }}>
                        ✓ {(results[idx].ingredients || []).length} found
                      </p>
                    </div>
                  )}
                  {results[idx]?.error && (
                    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0,
                      background: "rgba(239,68,68,0.85)", padding: "4px 8px" }}>
                      <p style={{ fontSize: "0.68rem", color: "#fff" }}>⚠ Error</p>
                    </div>
                  )}
                  <button onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                    style={{ position: "absolute", top: 6, right: 6, width: 22, height: 22,
                      borderRadius: "50%", background: "rgba(0,0,0,0.55)", border: "none",
                      color: "white", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <X size={11} />
                  </button>
                </motion.div>
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

      {loading && (
        <RecipeGenerationLoader
          title="Analyzing your ingredient photos"
          description="We're identifying ingredients, comparing recipe matches, and preparing the best dishes for you."
          steps={[
            { label: "Scanning images", Icon: ImageIcon },
            { label: "Detecting ingredients", Icon: ChefHat },
            { label: "Ranking recipes", Icon: ArrowRight },
          ]}
        />
      )}

      {allIngredients.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
          style={{ ...CARD, marginBottom: 14, border: "1px solid rgba(74,158,107,0.3)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <ChefHat size={16} color="#4a9e6b" />
            <span style={{ fontWeight: 700, color: "#4a9e6b", fontSize: "0.9rem" }}>Detected Ingredients ({allIngredients.length})</span>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {allIngredients.map((item, i) => (
              <span key={i} style={{ padding: "5px 12px", borderRadius: 20, fontSize: "0.78rem", fontWeight: 500,
                background: "rgba(74,158,107,0.12)", color: "#2d6a4a", border: "1px solid rgba(74,158,107,0.3)" }}>
                {item}
              </span>
            ))}
          </div>
        </motion.div>
      )}

      {allRecipes.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
          style={{ ...CARD, border: "1px solid rgba(200,135,58,0.3)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
            <ChefHat size={16} color="#C8873A" />
            <span style={{ fontWeight: 700, color: "#C8873A", fontSize: "0.9rem" }}>
              Recommended Recipes ({allRecipes.length}) — tap to view
            </span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {allRecipes.map((recipe, i) => (
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
                    <RecipeImage
                      name={recipe.name || recipe}
                      ingredients={recipe.ingredients || recipe.matched_ingredients || allIngredients}
                      alt={recipe.name || recipe}
                      style={{ width: 48, height: 48, borderRadius: 10, objectFit: "cover", flexShrink: 0 }}
                      loading="lazy"
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

      {files.length > 0 && (
        <motion.button initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          onClick={handleSubmit} disabled={loading}
          whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
          style={{ marginTop: 14, width: "100%", padding: "13px", borderRadius: 14,
            border: "none", cursor: loading ? "not-allowed" : "pointer",
            background: loading ? "rgba(74,158,107,0.4)" : "#4a9e6b",
            color: "#fff", fontSize: "0.95rem", fontWeight: 700, fontFamily: "inherit",
            display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
          {loading
            ? <><Loader2 size={16} style={{ animation: "spin 1s linear infinite" }} /> Analyzing...</>
            : <><ChefHat size={16} /> Generate Recipe ({files.length} image{files.length > 1 ? "s" : ""})</>}
        </motion.button>
      )}
    </div>
  );
}
