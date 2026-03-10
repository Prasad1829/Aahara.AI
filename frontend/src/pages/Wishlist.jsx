import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Clock, Leaf, Flame, Heart } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
export default function Wishlist() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_BASE}/wishlist`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to load wishlist");
        if (!cancelled) setItems(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) setError(err.message || "Failed to load wishlist");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, []);

  const goToRecipe = (recipe) => {
    navigate(`/recipe/${encodeURIComponent(recipe.name)}`, {
      state: { recipe },
    });
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "40px 24px 80px" }}>
      {loading && (
        <div style={{ marginTop: 16, padding: "18px 20px", borderRadius: 16,
          background: "rgba(250,246,237,0.97)", color: "#6b7280" }}>
          Loading wishlist...
        </div>
      )}

      {error && (
        <div style={{ marginTop: 16, padding: "14px 18px", borderRadius: 12,
          background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)",
          color: "#dc2626", fontSize: "0.85rem" }}>
          {error}
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div style={{ marginTop: 16, padding: "18px 20px", borderRadius: 16,
          background: "rgba(250,246,237,0.97)", color: "#6b7280" }}>
          No recipes in your wishlist yet.
        </div>
      )}

      {!loading && !error && items.length > 0 && (
        <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 12 }}>
          {items.map((recipe, i) => (
            <motion.div key={recipe.id ?? recipe.name ?? i}
              initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              whileHover={{ x: 4 }} whileTap={{ scale: 0.99 }}
              onClick={() => goToRecipe(recipe)}
              style={{ padding: "14px 16px", borderRadius: 14, cursor: "pointer",
                background: "rgba(250,246,237,0.97)", border: "1px solid rgba(200,135,58,0.2)",
                transition: "all 0.2s" }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(250,246,237,1)";
                e.currentTarget.style.border = "1px solid rgba(200,135,58,0.45)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "rgba(250,246,237,0.97)";
                e.currentTarget.style.border = "1px solid rgba(200,135,58,0.2)";
              }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
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
                </div>
                <ArrowRight size={17} style={{ color: "#C8873A", marginLeft: 10 }} />
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
