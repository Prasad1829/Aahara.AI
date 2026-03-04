import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, Salad, Check, Loader2, ChefHat, ArrowRight, Clock, Leaf, Flame } from "lucide-react";
import Navbar from "../components/Navbar";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const BG = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1920&q=80";

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
      const ingredients = [...selected].map((id) => VEGETABLES.find((v) => v.id === id)?.name);
      const res = await fetch(`${API_BASE}/get-recipes`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ ingredients }),
      });
      setResult(await res.json());
    } catch { setResult({ error: "Failed to fetch recipes." }); }
    finally { setLoading(false); }
  };

  const CARD = { background: "rgba(250,246,237,0.97)", borderRadius: 20, padding: 24, backdropFilter: "blur(8px)" };

  return (
    <div style={{ minHeight: "100vh", position: "relative" }}>
      <div style={{ position: "fixed", inset: 0,
        backgroundImage: `linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.6)), url('${BG}')`,
        backgroundSize: "cover", backgroundPosition: "center", zIndex: 0 }} />
      <div style={{ position: "relative", zIndex: 1 }}>
        <Navbar />
        <div style={{ maxWidth: 1000, margin: "0 auto", padding: "40px 24px 80px" }}>

          <motion.button initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }}
            onClick={() => navigate("/dashboard")}
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.82rem",
              color: "rgba(255,255,255,0.7)", background: "none", border: "none", cursor: "pointer", marginBottom: 24 }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "rgba(255,255,255,0.7)")}>
            <ArrowLeft size={15} /> Back to Dashboard
          </motion.button>

          {/* Header */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
            style={{ ...CARD, marginBottom: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <div style={{ width: 52, height: 52, borderRadius: 14,
                background: "rgba(200,135,58,0.15)", border: "1px solid rgba(200,135,58,0.3)",
                display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Salad size={22} color="#C8873A" />
              </div>
              <div>
                <h1 style={{ fontFamily: '"Playfair Display", Georgia, serif',
                  fontSize: "1.8rem", fontWeight: 900, color: "#2d2d2d", margin: 0 }}>
                  Select Vegetables
                </h1>
                <p style={{ color: "#6b7280", fontSize: "0.88rem", margin: "4px 0 0" }}>
                  Tap to select.{" "}
                  <span style={{ color: "#C8873A", fontWeight: 600 }}>
                    {selected.size > 0 ? `${selected.size} selected` : "None selected yet"}
                  </span>
                </p>
              </div>
            </div>
          </motion.div>

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
              <p style={{ fontSize: "0.85rem", color: "#4b5563", lineHeight: 1.7, whiteSpace: "pre-line" }}>
                {result.recipes || result.message || JSON.stringify(result, null, 2)}
              </p>
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
      </div>
    </div>
  );
}