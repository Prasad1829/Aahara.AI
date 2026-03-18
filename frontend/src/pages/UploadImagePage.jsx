import { useCallback, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, X, ImageIcon, Loader2, ChefHat, Plus, ArrowRight } from "lucide-react";
import RecipeGenerationLoader from "../components/RecipeGenerationLoader";
import RecipeRecommendationSection from "../components/RecipeRecommendationSection";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function UploadImagePage() {
  const navigate = useNavigate();
  const location = useLocation();
  const restoredState = location.state?.restoreState;
  const [files, setFiles] = useState(restoredState?.files || []);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(restoredState?.results || []);
  const [recommendedRecipes, setRecommendedRecipes] = useState(restoredState?.recommendedRecipes || []);
  const [additionalRecipes, setAdditionalRecipes] = useState(restoredState?.additionalRecipes || []);
  const [error, setError] = useState(restoredState?.error || null);
  const [dragOver, setDragOver] = useState(false);

  const addFiles = (newFiles) => {
    const images = Array.from(newFiles).filter((f) => f.type.startsWith("image/"));
    setFiles((prev) => [...prev, ...images.map((f) => ({ file: f, preview: URL.createObjectURL(f) }))]);
    setResults([]);
    setRecommendedRecipes([]);
    setAdditionalRecipes([]);
    setError(null);
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
    setResults([]);
    setRecommendedRecipes([]);
    setAdditionalRecipes([]);
  };

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    addFiles(e.dataTransfer.files);
  }, []);

  const handleSubmit = async () => {
    const uploadableFiles = files.filter((entry) => entry?.file);
    if (uploadableFiles.length === 0) return;
    setLoading(true);
    setError(null);
    setResults([]);
    setRecommendedRecipes([]);
    setAdditionalRecipes([]);
    try {
      const token = localStorage.getItem("token");
      const allResults = [];
      for (const { file } of uploadableFiles) {
        const formData = new FormData();
        formData.append("file", file);
        const res = await fetch(`${API_BASE}/upload`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        });
        const data = await res.json();
        if (!res.ok) {
          allResults.push({ error: data.detail || "Upload failed" });
        } else {
          allResults.push({
            ingredients: data.detected_ingredients || [],
            recommended: data.recommended_recipes || [],
            additional: data.additional_recipes || [],
          });
        }
      }
      setResults(allResults);

      const combinedIngredients = [...new Set(allResults.flatMap((r) => r.ingredients || []))];
      if (combinedIngredients.length > 0) {
        const res = await fetch(`${API_BASE}/recommend?ingredients=${encodeURIComponent(combinedIngredients.join(","))}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (res.ok) {
          setRecommendedRecipes(data.recommended_recipes || []);
          setAdditionalRecipes(data.additional_recipes || []);
        } else {
          setRecommendedRecipes([]);
          setAdditionalRecipes([]);
        }
      }
    } catch (err) {
      setError("Network error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const allIngredients = [...new Set(results.flatMap((r) => r.ingredients || []))];

  const goToRecipe = (recipe) => {
    const filesForRestore = files.map((entry) => ({
      preview: entry.preview,
      name: entry.file?.name || entry.name || "image",
    }));

    navigate(`/recipe/${encodeURIComponent(recipe.name || recipe)}`, {
      state: {
        recipe,
        detectedIngredients: allIngredients,
        returnTo: {
          path: "/upload-image",
          state: {
            files: filesForRestore,
            results,
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

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} style={{ ...CARD, marginBottom: 14 }}>
        <div
          onDrop={onDrop}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onClick={() => document.getElementById("file-input").click()}
          style={{
            border: `2px dashed ${dragOver ? "#4a9e6b" : "rgba(74,158,107,0.35)"}`,
            borderRadius: 14,
            padding: files.length > 0 ? "14px" : "40px 24px",
            textAlign: "center",
            cursor: "pointer",
            background: dragOver ? "rgba(74,158,107,0.06)" : "rgba(74,158,107,0.02)",
            transition: "all 0.2s",
          }}
        >
          {files.length === 0 ? (
            <>
              <ImageIcon size={34} style={{ color: "#4a9e6b", opacity: 0.5, marginBottom: 10 }} />
              <p style={{ fontSize: "0.95rem", fontWeight: 600, color: "#2d2d2d", marginBottom: 4 }}>Drop images here</p>
              <p style={{ fontSize: "0.78rem", color: "#9ca3af" }}>or click to browse - JPG, PNG, WEBP</p>
            </>
          ) : (
            <div style={{ display: "flex", alignItems: "center", gap: 8, justifyContent: "center", color: "#4a9e6b", fontSize: "0.88rem", fontWeight: 600 }}>
              <Plus size={16} /> Add more images
            </div>
          )}
          <input
            id="file-input"
            type="file"
            accept="image/*"
            multiple
            style={{ display: "none" }}
            onChange={(e) => {
              addFiles(e.target.files);
              e.target.value = "";
            }}
          />
        </div>

        <AnimatePresence>
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))", gap: 10, marginTop: 12 }}
            >
              {files.map(({ preview, file, name }, idx) => (
                <motion.div
                  key={preview}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  style={{ position: "relative", borderRadius: 10, overflow: "hidden", border: "1px solid rgba(74,158,107,0.3)" }}
                >
                  <img src={preview} alt={file?.name || name || `Upload ${idx + 1}`} style={{ width: "100%", height: 100, objectFit: "cover", display: "block" }} />
                  {results[idx] && !results[idx].error && (
                    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, background: "rgba(74,158,107,0.85)", padding: "4px 8px" }}>
                      <p style={{ fontSize: "0.68rem", color: "#fff", fontWeight: 600 }}>
                        Found {(results[idx].ingredients || []).length} ingredient(s)
                      </p>
                    </div>
                  )}
                  {results[idx]?.error && (
                    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, background: "rgba(239,68,68,0.85)", padding: "4px 8px" }}>
                      <p style={{ fontSize: "0.68rem", color: "#fff" }}>Error</p>
                    </div>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile(idx);
                    }}
                    style={{
                      position: "absolute",
                      top: 6,
                      right: 6,
                      width: 22,
                      height: 22,
                      borderRadius: "50%",
                      background: "rgba(0,0,0,0.55)",
                      border: "none",
                      color: "white",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <X size={11} />
                  </button>
                </motion.div>
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
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ ...CARD, marginBottom: 14, border: "1px solid rgba(74,158,107,0.3)" }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <ChefHat size={16} color="#4a9e6b" />
            <span style={{ fontWeight: 700, color: "#4a9e6b", fontSize: "0.9rem" }}>Detected Ingredients ({allIngredients.length})</span>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {allIngredients.map((item, i) => (
              <span
                key={i}
                style={{
                  padding: "5px 12px",
                  borderRadius: 20,
                  fontSize: "0.78rem",
                  fontWeight: 500,
                  background: "rgba(74,158,107,0.12)",
                  color: "#2d6a4a",
                  border: "1px solid rgba(74,158,107,0.3)",
                }}
              >
                {item}
              </span>
            ))}
          </div>
        </motion.div>
      )}

      <RecipeRecommendationSection
        title="Recommended Recipes"
        recipes={recommendedRecipes}
        ingredientsFallback={allIngredients}
        onRecipeClick={goToRecipe}
        cardStyle={CARD}
      />

      <RecipeRecommendationSection
        title="You can try these recipes by adding other ingredients"
        recipes={additionalRecipes}
        ingredientsFallback={allIngredients}
        onRecipeClick={goToRecipe}
        variant="additional"
        cardStyle={CARD}
      />

      {files.some((entry) => entry?.file) && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={handleSubmit}
          disabled={loading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          style={{
            marginTop: 14,
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
            ? <><Loader2 size={16} style={{ animation: "spin 1s linear infinite" }} /> Analyzing...</>
            : <><ChefHat size={16} /> Generate Recipe ({files.length} image{files.length > 1 ? "s" : ""})</>}
        </motion.button>
      )}
    </div>
  );
}
