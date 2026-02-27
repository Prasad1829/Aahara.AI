import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { History, LayoutDashboard, Settings, User } from "lucide-react";
import LoadingButton from "../components/LoadingButton";
import CircularSlider from "../components/CircularSlider";
import UploadPanel from "../components/UploadPanel";
import DetectionResult from "../components/DetectionResult";
import RecipeList from "../components/RecipeList";

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

export default function Dashboard() {
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
        <UploadPanel files={files} setFiles={setFiles} onUpload={handleUpload} loading={loading} />

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
                    <>
                      <DetectionResult
                        detected_ingredients={entry.payload?.detected_ingredients}
                        detection={entry.payload?.detection}
                      />
                      <RecipeList
                        recommended_recipes={entry.payload?.recommended_recipes}
                        blockKey={`batch-${entry.fileName}-${index}`}
                        savedRecipes={savedRecipes}
                        onToggleSave={toggleSavedRecipe}
                      />
                    </>
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
                <DetectionResult
                  detected_ingredients={manualResult?.detected_ingredients}
                  detection={manualResult?.detection}
                />
                <RecipeList
                  recommended_recipes={manualResult?.recommended_recipes}
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

