import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Heart, History, LayoutDashboard, Settings, User } from "lucide-react";
import AnimatedCard from "../components/AnimatedCard";
import LoadingButton from "../components/LoadingButton";
import CircularSlider from "../components/CircularSlider";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const vegetableOptions = [
  {
    name: "tomato",
    src: "/vegetables/tomato.jpg",
  },
  {
    name: "carrot",
    src: "/vegetables/carrot.jpg",
  },
  {
    name: "potato",
    src: "/vegetables/potato.jpg",
  },
  {
    name: "capsicum",
    src: "/vegetables/capsicum.jpg",
  },
  {
    name: "onion",
    src: "/vegetables/onion.jpg",
  },
  {
    name: "cucumber",
    src: "/vegetables/cucumber.jpg",
  },
  {
    name: "cauliflower",
    src: "/vegetables/cauliflower.jpg",
  },
  {
    name: "cabbage",
    src: "/vegetables/cabbage.jpg",
  },
];

function AIProcessingIndicator() {
  return (
    <div className="mt-3 rounded-xl border border-blue-200/70 bg-blue-50/70 p-3">
      <div className="flex items-center gap-3">
        <span className="spinner border-blue-300 border-t-blue-600" />
        <div>
          <p className="text-sm font-semibold text-blue-900">AI is processing images</p>
          <p className="text-xs text-blue-700">Detecting ingredients and ranking recipes...</p>
        </div>
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-blue-100">
        <motion.div
          className="h-full w-1/3 bg-gradient-to-r from-transparent via-blue-400/70 to-transparent"
          initial={{ x: "-120%" }}
          animate={{ x: "350%" }}
          transition={{ duration: 1.3, ease: "linear", repeat: Infinity }}
          style={{ willChange: "transform" }}
        />
      </div>
    </div>
  );
}

const RecipeItem = memo(function RecipeItem({ recipe, recipeKey, isSaved, onToggleSave, delay }) {
  const scorePct = Math.round((recipe.match_score || 0) * 100);

  return (
    <AnimatedCard delay={delay} className="p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-extrabold text-xl text-stone-900">{recipe.name}</h3>
          <p className="text-sm text-stone-600 mt-1">
            {recipe.is_veg ? "Veg" : "Non-Veg"} · {recipe.cooking_time_minutes} mins
          </p>
        </div>

        <motion.button
          onClick={() => onToggleSave(recipeKey)}
          whileTap={{ scale: 0.85 }}
          animate={isSaved ? { scale: [1, 1.2, 1] } : { scale: 1 }}
          transition={{ duration: 0.25 }}
          className={`rounded-full p-2 border min-h-11 min-w-11 ${
            isSaved ? "border-rose-300 bg-rose-50 text-rose-600" : "border-stone-200 bg-white text-stone-500"
          }`}
          aria-label={isSaved ? "Unsave recipe" : "Save recipe"}
          style={{ willChange: "transform, opacity" }}
        >
          <Heart size={18} fill={isSaved ? "currentColor" : "none"} />
        </motion.button>
      </div>

      <div className="mt-4">
        <div className="flex justify-between text-sm text-stone-700 mb-1">
          <span className="font-semibold">Ingredient Match</span>
          <span className="font-bold">{scorePct}%</span>
        </div>
        <div className="h-2.5 rounded-full bg-stone-200 overflow-hidden">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-green-400"
            initial={{ scaleX: 0, transformOrigin: "left center" }}
            animate={{ scaleX: Math.max(0.02, scorePct / 100) }}
            transition={{ duration: 0.7, delay: delay + 0.08 }}
            style={{ willChange: "transform, opacity" }}
          />
        </div>
      </div>

      <div className="mt-3 text-sm text-stone-700">
        <p>
          <span className="font-semibold">Matched:</span> {recipe.matched_ingredients.join(", ") || "-"}
        </p>
      </div>

      <div className="mt-2">
        <p className="text-sm font-semibold text-stone-800 mb-1">Missing</p>
        <div className="flex flex-wrap gap-1.5">
          {recipe.missing_ingredients?.length > 0 ? (
            recipe.missing_ingredients.map((item, idx) => (
              <motion.span
                key={`${item}-${idx}`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, delay: delay + idx * 0.03 }}
                className="inline-flex items-center rounded-full border border-rose-300 bg-rose-50 px-2.5 py-1 text-xs font-medium text-rose-700"
                style={{ willChange: "transform, opacity" }}
              >
                {item}
              </motion.span>
            ))
          ) : (
            <span className="text-sm text-emerald-700">No missing ingredients</span>
          )}
        </div>
      </div>

      {recipe.instructions?.length > 0 && (
        <div className="mt-4">
          <p className="font-bold text-stone-900">Instructions</p>
          <ol className="list-decimal list-inside text-stone-700 mt-1 space-y-1 text-sm">
            {recipe.instructions.map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ol>
        </div>
      )}
    </AnimatedCard>
  );
});

const RecipeBlock = memo(function RecipeBlock({ payload, blockKey, savedRecipes, onToggleSave }) {
  if (!payload) return null;
  const detected = payload.detected_ingredients || [];

  return (
    <motion.div layout transition={{ duration: 0.25 }} className="mt-4">
      <h2 className="font-bold text-lg text-stone-900 mb-2">Detected Ingredients</h2>
      <div className="flex flex-wrap gap-2">
        {detected.length > 0 ? (
          detected.map((ingredient, idx) => (
            <motion.span
              key={`${ingredient}-${idx}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: idx * 0.04 }}
              className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-sm text-stone-700"
              style={{ willChange: "transform, opacity" }}
            >
              {ingredient}
            </motion.span>
          ))
        ) : (
          <p className="text-stone-700">No ingredients detected.</p>
        )}
      </div>

      {payload.detection && (
        <p className="mt-2 text-sm text-stone-600">
          Source: <span className="font-semibold">{payload.detection.source || "n/a"}</span>, Confidence:{" "}
          <span className="font-semibold">{Math.round((payload.detection.confidence || 0) * 100)}%</span>
        </p>
      )}

      {payload.detection?.top_predictions?.length > 0 && (
        <div className="mt-3 rounded-lg border border-stone-200 bg-stone-50 p-3">
          <p className="text-sm font-semibold text-stone-800">Top Predictions</p>
          <ul className="mt-1 text-sm text-stone-700 space-y-1">
            {payload.detection.top_predictions.map((pred, idx) => (
              <li key={`${pred.ingredient}-${idx}`}>
                {idx + 1}. {pred.ingredient} ({Math.round((pred.confidence || 0) * 100)}%)
              </li>
            ))}
          </ul>
          {(payload.detection.confidence || 0) < 0.6 && (
            <p className="mt-2 text-xs text-amber-700">
              Prediction confidence is low. Use manual ingredient correction.
            </p>
          )}
        </div>
      )}

      <h2 className="font-bold text-lg text-stone-900 mt-6 mb-3">Recommended Recipes</h2>
      {(!payload.recommended_recipes || payload.recommended_recipes.length === 0) && (
        <p className="text-stone-600">No recipe matches found. Try another image.</p>
      )}

      <div className="space-y-4">
        <AnimatePresence>
          {payload.recommended_recipes?.map((recipe, index) => {
            const recipeKey = `${blockKey}-${recipe.name}-${index}`;
            return (
              <motion.div
                key={recipeKey}
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.28, delay: index * 0.05 }}
                style={{ willChange: "transform, opacity" }}
              >
                <RecipeItem
                  recipe={recipe}
                  recipeKey={recipeKey}
                  isSaved={savedRecipes.includes(recipeKey)}
                  onToggleSave={onToggleSave}
                  delay={index * 0.04}
                />
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </motion.div>
  );
});

export default function Dashboard() {
  const fileInputRef = useRef(null);
  const [files, setFiles] = useState([]);
  const [manualResult, setManualResult] = useState(null);
  const [batchResults, setBatchResults] = useState([]);
  const [savedRecipes, setSavedRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [manualIngredients, setManualIngredients] = useState("");
  const [selectedVeggies, setSelectedVeggies] = useState([]);
  const [manualLoading, setManualLoading] = useState(false);
  const [errorState, setErrorState] = useState({ message: "", context: "" });
  const [dragActive, setDragActive] = useState(false);
  const [activeMenu, setActiveMenu] = useState("dashboard");
  const [recipeHistory, setRecipeHistory] = useState([]);
  const [settingsState, setSettingsState] = useState(() => {
    try {
      const raw = localStorage.getItem("ahara_settings");
      return raw ? JSON.parse(raw) : { compactMode: false, autoScrollToResults: true };
    } catch {
      return { compactMode: false, autoScrollToResults: true };
    }
  });

  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) {
      navigate("/login");
    } else {
      fetchCurrentUser();
    }
  }, []);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("ahara_recipe_history");
      if (raw) setRecipeHistory(JSON.parse(raw));
    } catch {
      setRecipeHistory([]);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("ahara_recipe_history", JSON.stringify(recipeHistory.slice(0, 40)));
  }, [recipeHistory]);

  useEffect(() => {
    localStorage.setItem("ahara_settings", JSON.stringify(settingsState));
  }, [settingsState]);

  const fetchCurrentUser = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        localStorage.removeItem("token");
        navigate("/login");
        return;
      }

      const data = await response.json();
      setUser(data);
    } catch {
      setErrorState({ message: "Failed to load user profile.", context: "general" });
    }
  };

  const parseErrorMessage = (payload, fallback) => {
    if (!payload) return fallback;
    if (typeof payload === "string") return payload;
    if (typeof payload.detail === "string") return payload.detail;
    if (Array.isArray(payload.detail) && payload.detail.length > 0) {
      const first = payload.detail[0];
      if (typeof first === "string") return first;
      if (first && first.msg) return first.msg;
    }
    return fallback;
  };

  const addFiles = (incoming) => {
    const arr = Array.from(incoming || []);
    if (arr.length === 0) return;

    const deduped = arr.filter(
      (candidate) =>
        !files.some((existing) => existing.name === candidate.name && existing.size === candidate.size)
    );
    setFiles((prev) => [...prev, ...deduped]);
  };

  const removeFile = (name) => {
    setFiles((prev) => prev.filter((f) => f.name !== name));
  };

  const toggleVeggie = (name) => {
    setSelectedVeggies((prev) =>
      prev.includes(name) ? prev.filter((v) => v !== name) : [...prev, name]
    );
  };

  const toggleSavedRecipe = (recipeKey) => {
    setSavedRecipes((prev) =>
      prev.includes(recipeKey) ? prev.filter((key) => key !== recipeKey) : [...prev, recipeKey]
    );
  };

  const applySelectedVeggies = () => {
    if (selectedVeggies.length === 0) {
      setErrorState({ message: "Select at least one vegetable from the arc.", context: "manual" });
      return;
    }

    const merged = new Set(
      manualIngredients
        .split(",")
        .map((x) => x.trim().toLowerCase())
        .filter(Boolean)
    );

    selectedVeggies.forEach((v) => merged.add(v));
    setManualIngredients(Array.from(merged).join(", "));
    setErrorState({ message: "", context: "" });
  };

  const handleUpload = useCallback(async () => {
    if (loading) return;
    if (files.length === 0) {
      setErrorState({ message: "Please select at least one image.", context: "upload" });
      return;
    }

    try {
      setLoading(true);
      setErrorState({ message: "", context: "" });
      setBatchResults([]);
      setManualResult(null);

      const results = [];

      for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_BASE}/upload`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        });

        if (response.status === 401) {
          setErrorState({ message: "Session expired. Please login again.", context: "upload" });
          localStorage.removeItem("token");
          navigate("/login");
          return;
        }

        const data = await response.json();
        if (!response.ok) {
          results.push({
            fileName: file.name,
            ok: false,
            error: parseErrorMessage(data, "Upload failed"),
          });
        } else {
          results.push({
            fileName: file.name,
            ok: true,
            payload: data,
          });
        }
      }

      setBatchResults(results);
      const fresh = results
        .filter((r) => r.ok && r.payload?.recommended_recipes?.length > 0)
        .flatMap((r) =>
          r.payload.recommended_recipes.map((recipe) => ({
            id: `${Date.now()}-${r.fileName}-${recipe.name}`,
            recipeName: recipe.name,
            source: `Image: ${r.fileName}`,
            timestamp: new Date().toISOString(),
            matchScore: Math.round((recipe.match_score || 0) * 100),
          }))
        );
      if (fresh.length > 0) setRecipeHistory((prev) => [...fresh, ...prev].slice(0, 40));
    } catch {
      setErrorState({ message: "Upload failed. Check backend connection.", context: "upload" });
    } finally {
      setLoading(false);
    }
  }, [files, loading, navigate, token]);

  const handleManualRecommend = useCallback(async () => {
    if (manualLoading) return;
    const cleaned = manualIngredients
      .split(",")
      .map((x) => x.trim().toLowerCase())
      .filter(Boolean)
      .join(",");

    if (!cleaned) {
      setErrorState({ message: "Enter at least one ingredient (comma separated).", context: "manual" });
      return;
    }

    try {
      setManualLoading(true);
      setErrorState({ message: "", context: "" });

      const response = await fetch(
        `${API_BASE}/recommend?ingredients=${encodeURIComponent(cleaned)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 401) {
        setErrorState({ message: "Session expired. Please login again.", context: "manual" });
        localStorage.removeItem("token");
        navigate("/login");
        return;
      }

      const data = await response.json();
      if (!response.ok) {
        setErrorState({
          message: parseErrorMessage(data, "Could not fetch recommendations."),
          context: "manual",
        });
        return;
      }

      setManualResult({
        ...data,
        detection: {
          status: "manual",
          source: "manual",
          confidence: 1,
          top_predictions: [],
        },
      });
      if (data?.recommended_recipes?.length > 0) {
        const fresh = data.recommended_recipes.map((recipe) => ({
          id: `${Date.now()}-manual-${recipe.name}`,
          recipeName: recipe.name,
          source: `Manual: ${cleaned}`,
          timestamp: new Date().toISOString(),
          matchScore: Math.round((recipe.match_score || 0) * 100),
        }));
        setRecipeHistory((prev) => [...fresh, ...prev].slice(0, 40));
      }
    } catch {
      setErrorState({ message: "Failed to get manual recommendations.", context: "manual" });
    } finally {
      setManualLoading(false);
    }
  }, [manualIngredients, manualLoading, navigate, token]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const retryAction = useMemo(() => {
    if (errorState.context === "upload") return handleUpload;
    if (errorState.context === "manual") return handleManualRecommend;
    return null;
  }, [errorState.context, handleManualRecommend, handleUpload]);

  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "profile", label: "Profile", icon: User },
    { id: "history", label: "History", icon: History },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <div className="app-animated-bg relative min-h-screen overflow-hidden px-4 py-6 md:py-8">
      <div className="relative z-10 mx-auto w-full max-w-5xl rounded-3xl border border-white/70 bg-white/65 backdrop-blur-xl shadow-2xl p-4 md:p-8">
        <div className="mb-4 flex items-center justify-between gap-3">
          <p className="text-sm font-medium text-stone-700">
            Welcome, <span className="font-bold text-stone-900">{user?.email || "User"}</span>
          </p>
          <button
            onClick={handleLogout}
            className="motion-btn min-h-11 rounded-xl bg-rose-500 px-4 py-2 font-semibold text-white transition hover:bg-rose-600"
          >
            Logout
          </button>
        </div>

        <div className="mb-4 grid grid-cols-2 gap-2 rounded-2xl border border-zinc-800 bg-zinc-900 p-2 sm:grid-cols-4">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = activeMenu === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveMenu(item.id)}
                className={`motion-btn min-h-11 rounded-xl px-3 py-2 text-sm font-semibold ${
                  active ? "bg-amber-400 text-zinc-900" : "bg-zinc-800 text-zinc-200 hover:bg-zinc-700"
                }`}
              >
                <span className="inline-flex items-center gap-2">
                  <Icon size={16} />
                  {item.label}
                </span>
              </button>
            );
          })}
        </div>

        {activeMenu === "profile" && (
          <motion.section
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4 rounded-2xl border border-zinc-800 bg-zinc-900 p-5 text-zinc-200"
          >
            <h3 className="text-xl font-bold text-white">Profile</h3>
            <p className="mt-2 text-sm">Email: {user?.email || "Not available"}</p>
            <p className="mt-1 text-sm">Saved recipes: {savedRecipes.length}</p>
            <p className="mt-1 text-sm">History items: {recipeHistory.length}</p>
          </motion.section>
        )}

        {activeMenu === "history" && (
          <motion.section
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4 rounded-2xl border border-zinc-800 bg-zinc-900 p-5 text-zinc-200"
          >
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-xl font-bold text-white">Recipe History</h3>
              <button
                onClick={() => setRecipeHistory([])}
                className="motion-btn min-h-10 rounded-lg bg-zinc-800 px-3 py-1.5 text-sm font-semibold text-zinc-100 hover:bg-zinc-700"
              >
                Clear
              </button>
            </div>
            {recipeHistory.length === 0 ? (
              <p className="mt-3 text-sm text-zinc-400">No history yet. Generate recipes to see activity.</p>
            ) : (
              <div className="mt-3 max-h-56 space-y-2 overflow-auto pr-1">
                {recipeHistory.map((item) => (
                  <div key={item.id} className="rounded-xl border border-zinc-800 bg-zinc-950 p-3">
                    <p className="font-semibold text-white">{item.recipeName}</p>
                    <p className="text-xs text-zinc-400">{item.source}</p>
                    <p className="text-xs text-zinc-500">
                      {new Date(item.timestamp).toLocaleString()} - Match {item.matchScore}%
                    </p>
                  </div>
                ))}
              </div>
            )}
          </motion.section>
        )}

        {activeMenu === "settings" && (
          <motion.section
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4 rounded-2xl border border-zinc-800 bg-zinc-900 p-5 text-zinc-200"
          >
            <h3 className="text-xl font-bold text-white">Settings</h3>
            <div className="mt-3 space-y-3">
              <label className="flex items-center justify-between rounded-lg border border-zinc-800 bg-zinc-950 p-3">
                <span className="text-sm">Compact result cards</span>
                <input
                  type="checkbox"
                  checked={settingsState.compactMode}
                  onChange={(e) =>
                    setSettingsState((prev) => ({ ...prev, compactMode: e.target.checked }))
                  }
                />
              </label>
              <label className="flex items-center justify-between rounded-lg border border-zinc-800 bg-zinc-950 p-3">
                <span className="text-sm">Auto scroll to results</span>
                <input
                  type="checkbox"
                  checked={settingsState.autoScrollToResults}
                  onChange={(e) =>
                    setSettingsState((prev) => ({ ...prev, autoScrollToResults: e.target.checked }))
                  }
                />
              </label>
            </div>
          </motion.section>
        )}

        {activeMenu === "dashboard" && (
          <>
        <input
          type="file"
          accept="image/*"
          multiple
          ref={fileInputRef}
          onChange={(e) => addFiles(e.target.files)}
          className="hidden"
        />

        <section className="relative overflow-hidden rounded-2xl border border-white/60 bg-white/45 p-4 md:p-5 backdrop-blur-lg">
          <div className={loading ? "loading-shimmer" : ""} />
          <p className="text-sm font-semibold text-slate-800">Drag and drop multiple images here</p>
          <p className="mt-1 text-xs text-slate-600">or click Select Images to choose files</p>

          <div className="mt-3 flex flex-col gap-3 sm:flex-row">
            <button
              onClick={() => fileInputRef.current.click()}
              className="motion-btn min-h-11 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
            >
              Select Images
            </button>

            <LoadingButton
              onClick={handleUpload}
              loading={loading}
              label="Generate Recipe"
              loadingLabel="Analyzing..."
              className="bg-cyan-600 text-white hover:bg-cyan-700"
            />
          </div>

          {loading && <AIProcessingIndicator />}

          <div
            className={`mt-3 rounded-xl border-2 border-dashed p-3 text-xs text-slate-600 transition ${
              dragActive ? "border-blue-500 bg-blue-50" : "border-slate-300 bg-white/50"
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragActive(false);
              addFiles(e.dataTransfer.files);
            }}
          >
            Drop images here
          </div>
        </section>

        {files.length > 0 && (
          <motion.div layout transition={{ duration: 0.22 }} className="mt-4 rounded-xl border border-stone-200 bg-white p-4">
            <p className="mb-2 text-sm font-semibold text-stone-800">Selected Files ({files.length})</p>
            <div className="flex flex-wrap gap-2">
              {files.map((f) => (
                <div
                  key={`${f.name}-${f.size}`}
                  className="inline-flex min-h-10 items-center gap-2 rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm"
                >
                  <span className="text-slate-700">{f.name}</span>
                  <button
                    className="font-bold text-rose-600 min-h-8 min-w-8"
                    onClick={() => removeFile(f.name)}
                    aria-label={`Remove ${f.name}`}
                  >
                    x
                  </button>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        <section className="mt-5 overflow-hidden rounded-3xl border border-zinc-800 bg-zinc-950 p-4 text-zinc-100 md:p-7">
          <div className="flex flex-col items-stretch gap-6 md:flex-row">
            <div className="z-10 md:w-1/2">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-amber-300">Select Vegetables</p>
              <h2 className="mt-2 text-4xl font-black md:text-5xl text-white">AHARA AI</h2>
              <p className="mt-3 max-w-sm text-sm text-zinc-300 md:text-base">
                Vegetables rotate smoothly on the circular track. Tap any vegetable, then click
                <span className="font-bold"> Use Selected </span>
                to auto-fill ingredients.
              </p>
              <button
                onClick={applySelectedVeggies}
                className="motion-btn mt-5 min-h-11 rounded-xl bg-amber-400 px-5 py-2.5 font-bold text-zinc-900 hover:bg-amber-300"
              >
                Use Selected ({selectedVeggies.length})
              </button>
            </div>

            <div className="relative min-h-[260px] md:w-1/2">
              <CircularSlider
                items={vegetableOptions}
                selectedItems={selectedVeggies}
                onToggleItem={toggleVeggie}
              />
              <div className="mt-4 text-center text-xs text-zinc-400">
                {selectedVeggies.length > 0
                  ? `Selected: ${selectedVeggies.join(", ")}`
                  : "Tap a vegetable to select"}
              </div>
            </div>
          </div>
        </section>

        <section className="mt-4 rounded-xl border border-stone-200 bg-white/80 p-4 backdrop-blur-md">
          <p className="text-sm font-semibold text-stone-800">Detection wrong? Enter ingredients manually</p>
          <p className="mt-1 text-xs text-stone-600">Example: onion, tomato, potato</p>
          <div className="mt-3 flex flex-col gap-2 sm:flex-row">
            <input
              value={manualIngredients}
              onChange={(e) => setManualIngredients(e.target.value)}
              placeholder="Enter comma separated ingredients"
              className="flex-1 min-h-11 rounded-lg border border-stone-300 bg-white/90 px-3 py-2 outline-none transition focus:border-blue-400 focus:ring-4 focus:ring-blue-100"
            />
            <LoadingButton
              onClick={handleManualRecommend}
              loading={manualLoading}
              label="Generate Recipe"
              loadingLabel="Finding..."
              className="bg-blue-600 text-white hover:bg-blue-700"
            />
          </div>
        </section>

        <AnimatePresence>
          {errorState.message && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
              className="mt-4 rounded-lg border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-700"
            >
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <span>{errorState.message}</span>
                {retryAction && (
                  <button
                    onClick={retryAction}
                    className="motion-btn min-h-10 rounded-lg border border-rose-300 bg-white px-3 py-1.5 font-semibold text-rose-700 hover:bg-rose-100"
                  >
                    Retry
                  </button>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <motion.div layout transition={{ duration: 0.25 }}>
          {batchResults.length > 0 && (
            <div className="mt-6">
              <h2 className="mb-3 text-xl font-bold text-stone-900">Batch Upload Results</h2>
              {batchResults.map((entry, index) => (
                <motion.div
                  key={`${entry.fileName}-${index}`}
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.24, delay: index * 0.04 }}
                  className="mb-5 rounded-2xl border border-stone-200 bg-white/85 p-4 shadow-sm backdrop-blur-md"
                >
                  <p className="font-semibold text-stone-900">File: {entry.fileName}</p>
                  {!entry.ok && <p className="mt-1 text-sm text-rose-600">{entry.error}</p>}
                  {entry.ok && (
                    <RecipeBlock
                      payload={entry.payload}
                      blockKey={`batch-${entry.fileName}-${index}`}
                      savedRecipes={savedRecipes}
                      onToggleSave={toggleSavedRecipe}
                    />
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        <motion.div layout transition={{ duration: 0.25 }}>
          {manualResult && (
            <div className="mt-6">
              <h2 className="mb-3 text-xl font-bold text-stone-900">Manual Recommendation</h2>
              <div className="rounded-2xl border border-stone-200 bg-white/85 p-4 shadow-sm backdrop-blur-md">
                <RecipeBlock
                  payload={manualResult}
                  blockKey="manual"
                  savedRecipes={savedRecipes}
                  onToggleSave={toggleSavedRecipe}
                />
              </div>
            </div>
          )}
        </motion.div>
          </>
        )}
      </div>
    </div>
  );
}
