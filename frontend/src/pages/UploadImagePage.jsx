import { useCallback, useState, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, X, ImageIcon, Loader2, ChefHat, Plus, ArrowRight, Camera } from "lucide-react";
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
  const [showWebcam, setShowWebcam] = useState(false);
  const [stream, setStream] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

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

  // ── Stop camera stream completely ──
  const stopStream = (s) => {
    if (s) {
      s.getTracks().forEach((track) => {
        track.stop();
        track.enabled = false;
      });
    }
  };

  // ── Open Camera ──
  const openCamera = async (e) => {
    e.stopPropagation();
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
      });
      setStream(mediaStream);
      setShowWebcam(true);
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
          videoRef.current.play();
        }
      }, 100);
    } catch (err) {
      setError("Camera access denied. Please allow camera permission and try again.");
    }
  };

  // ── Close Camera — stream completely stop ──
  const closeWebcam = () => {
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.srcObject = null;
    }
    stopStream(stream);
    setStream(null);
    setShowWebcam(false);
  };

  // ── Capture Photo — camera auto close ──
  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    canvas.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], `camera_${Date.now()}.jpg`, { type: "image/jpeg" });
      const preview = URL.createObjectURL(blob);
      setFiles((prev) => [...prev, { file, preview }]);
      setResults([]);
      setRecommendedRecipes([]);
      setAdditionalRecipes([]);
      setError(null);
      // ── Camera auto close after capture ──
      closeWebcam();
    }, "image/jpeg", 0.92);
  };

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
        const res = await fetch(
          `${API_BASE}/recommend?ingredients=${encodeURIComponent(combinedIngredients.join(","))}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
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
          state: { files: filesForRestore, results, recommendedRecipes, additionalRecipes, error },
        },
      },
    });
  };

  const CARD = {
    background: "rgba(250,246,237,0.97)",
    borderRadius: 20,
    padding: 20,
    backdropFilter: "blur(8px)",
  };

  // ── OR + Take Picture button — always visible ──
  const CameraButton = () => (
    <div style={{ marginTop: 12 }} onClick={(e) => e.stopPropagation()}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, margin: "10px auto", maxWidth: 220 }}>
        <div style={{ flex: 1, height: 1, background: "rgba(0,0,0,0.15)" }} />
        <span style={{ fontSize: "0.8rem", color: "#9ca3af", fontWeight: 700, letterSpacing: "0.05em" }}>
          OR
        </span>
        <div style={{ flex: 1, height: 1, background: "rgba(0,0,0,0.15)" }} />
      </div>
      <button
        onClick={openCamera}
        style={{
          display: "inline-flex", alignItems: "center", gap: 6,
          padding: "9px 20px", borderRadius: 10, border: "none",
          background: "rgb(200, 135, 58)", color: "#ffffff",
          fontSize: "0.85rem", fontWeight: 700,
          cursor: "pointer", fontFamily: "inherit",
          boxShadow: "0 2px 8px rgba(200,135,58,0.35)",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.background = "rgb(176, 118, 45)")}
        onMouseLeave={(e) => (e.currentTarget.style.background = "rgb(200, 135, 58)")}
      >
        <Camera size={15} /> Take Picture
      </button>
    </div>
  );

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "24px 24px 80px" }}>
      <motion.button
        initial={{ opacity: 0, x: -12 }}
        animate={{ opacity: 1, x: 0 }}
        onClick={() => { closeWebcam(); navigate("/dashboard"); }}
        style={{
          display: "flex", alignItems: "center", gap: 6, fontSize: "0.82rem",
          color: "#ffffff", background: "rgba(255,255,255,0.15)",
          border: "1px solid rgba(255,255,255,0.3)", borderRadius: 8,
          padding: "6px 12px", cursor: "pointer", marginBottom: 20,
        }}
        onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.25)")}
        onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.15)")}
      >
        <ArrowLeft size={15} /> Back to Dashboard
      </motion.button>

      {/* ── Webcam Modal ── */}
      <AnimatePresence>
        {showWebcam && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            style={{ ...CARD, marginBottom: 14, border: "2px solid rgba(200,135,58,0.35)" }}
          >
            {/* Header */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
              <span style={{ fontWeight: 700, color: "#C8873A", fontSize: "0.95rem",
                display: "flex", alignItems: "center", gap: 6 }}>
                <Camera size={16} /> Camera
              </span>
              <button
                onClick={closeWebcam}
                style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
                  borderRadius: 8, padding: "4px 12px", cursor: "pointer", color: "#dc2626",
                  fontSize: "0.82rem", fontWeight: 700, fontFamily: "inherit" }}
              >
                ✕ Close
              </button>
            </div>

            {/* Tip */}
            <div style={{ display: "flex", alignItems: "center", gap: 8,
              padding: "10px 14px", borderRadius: 10, marginBottom: 10,
              background: "rgba(200,135,58,0.1)", border: "1px solid rgba(200,135,58,0.3)" }}>
              <span style={{ fontSize: "1rem" }}>💡</span>
              <p style={{ fontSize: "0.82rem", color: "#C8873A", fontWeight: 600, margin: 0 }}>
                Please capture one ingredient per photo for better detection.
              </p>
            </div>

            {/* Video */}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              style={{ width: "100%", borderRadius: 12, background: "#1a1a1a",
                maxHeight: 340, objectFit: "cover", display: "block" }}
            />
            <canvas ref={canvasRef} style={{ display: "none" }} />

            {/* Capture button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              onClick={capturePhoto}
              style={{ marginTop: 12, width: "100%", padding: "13px", borderRadius: 14,
                border: "none", background: "rgb(200, 135, 58)", color: "#fff",
                fontSize: "0.95rem", fontWeight: 700, cursor: "pointer", fontFamily: "inherit",
                display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}
            >
              <Camera size={18} /> 📸 Capture Photo
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Upload / Drop Zone ── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        style={{ ...CARD, marginBottom: 14 }}
      >
        <div
          onDrop={onDrop}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onClick={() => document.getElementById("file-input").click()}
          style={{
            border: `2px dashed ${dragOver ? "#4a9e6b" : "rgba(74,158,107,0.35)"}`,
            borderRadius: 14,
            padding: files.length > 0 ? "14px" : "40px 24px",
            textAlign: "center", cursor: "pointer",
            background: dragOver ? "rgba(74,158,107,0.06)" : "rgba(74,158,107,0.02)",
            transition: "all 0.2s",
          }}
        >
          {files.length === 0 ? (
            <>
              <ImageIcon size={34} style={{ color: "#4a9e6b", opacity: 0.5, marginBottom: 10 }} />
              <p style={{ fontSize: "0.95rem", fontWeight: 600, color: "#2d2d2d", marginBottom: 4 }}>
                Drop images here
              </p>
              <p style={{ fontSize: "0.78rem", color: "#9ca3af", marginBottom: 0 }}>
                or click to browse - JPG, PNG, WEBP
              </p>
              <CameraButton />
            </>
          ) : (
            <>
              <div style={{ display: "flex", alignItems: "center", gap: 8,
                justifyContent: "center", color: "#4a9e6b", fontSize: "0.88rem", fontWeight: 600 }}>
                <Plus size={16} /> Add more images
              </div>
              <CameraButton />
            </>
          )}
          <input
            id="file-input"
            type="file"
            accept="image/*"
            multiple
            style={{ display: "none" }}
            onChange={(e) => { addFiles(e.target.files); e.target.value = ""; }}
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
                  style={{ position: "relative", borderRadius: 10, overflow: "hidden",
                    border: "1px solid rgba(74,158,107,0.3)" }}
                >
                  <img
                    src={preview}
                    alt={file?.name || name || `Upload ${idx + 1}`}
                    style={{ width: "100%", height: 100, objectFit: "cover", display: "block" }}
                  />
                  {results[idx] && !results[idx].error && (
                    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0,
                      background: "rgba(74,158,107,0.85)", padding: "4px 8px" }}>
                      <p style={{ fontSize: "0.68rem", color: "#fff", fontWeight: 600 }}>
                        Found {(results[idx].ingredients || []).length} ingredient(s)
                      </p>
                    </div>
                  )}
                  {results[idx]?.error && (
                    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0,
                      background: "rgba(239,68,68,0.85)", padding: "4px 8px" }}>
                      <p style={{ fontSize: "0.68rem", color: "#fff" }}>Error</p>
                    </div>
                  )}
                  <button
                    onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                    style={{ position: "absolute", top: 6, right: 6, width: 22, height: 22,
                      borderRadius: "50%", background: "rgba(0,0,0,0.55)", border: "none",
                      color: "white", cursor: "pointer", display: "flex",
                      alignItems: "center", justifyContent: "center" }}
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

      {!loading && results.length > 0 && allIngredients.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ ...CARD, marginBottom: 14, border: "1px solid rgba(239,68,68,0.3)",
            textAlign: "center", padding: "32px 20px" }}
        >
          <div style={{ fontSize: "2.5rem", marginBottom: 12 }}>🔍</div>
          <h3 style={{ fontWeight: 700, color: "#dc2626", fontSize: "1rem", marginBottom: 8 }}>
            No Ingredients Found
          </h3>
          <p style={{ color: "#6b7280", fontSize: "0.85rem", lineHeight: 1.6 }}>
            We couldn't identify any ingredients in this image.<br />
            Please try uploading a clearer photo of your ingredients.
          </p>
          <p style={{ color: "#9ca3af", fontSize: "0.75rem", marginTop: 12 }}>
            💡 Try capturing one ingredient at a time for better detection
          </p>
        </motion.div>
      )}

      {allIngredients.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ ...CARD, marginBottom: 14, border: "1px solid rgba(74,158,107,0.3)" }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <ChefHat size={16} color="#4a9e6b" />
            <span style={{ fontWeight: 700, color: "#4a9e6b", fontSize: "0.9rem" }}>
              Detected Ingredients ({allIngredients.length})
            </span>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {allIngredients.map((item, i) => (
              <span key={i} style={{ padding: "5px 12px", borderRadius: 20, fontSize: "0.78rem",
                fontWeight: 500, background: "rgba(74,158,107,0.12)", color: "#2d6a4a",
                border: "1px solid rgba(74,158,107,0.3)" }}>
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
          style={{ marginTop: 14, width: "100%", padding: "13px", borderRadius: 14,
            border: "none", cursor: loading ? "not-allowed" : "pointer",
            background: loading ? "rgba(74,158,107,0.4)" : "#4a9e6b",
            color: "#fff", fontSize: "0.95rem", fontWeight: 700, fontFamily: "inherit",
            display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}
        >
          {loading
            ? <><Loader2 size={16} style={{ animation: "spin 1s linear infinite" }} /> Analyzing...</>
            : <><ChefHat size={16} /> Generate Recipe ({files.length} image{files.length > 1 ? "s" : ""})</>}
        </motion.button>
      )}
    </div>
  );
}