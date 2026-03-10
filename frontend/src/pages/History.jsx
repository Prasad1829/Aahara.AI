import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Clock, Leaf, Flame } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function History() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const CARD = {
    background: "rgba(250,246,237,0.97)",
    borderRadius: 20,
    padding: 24,
    backdropFilter: "blur(8px)",
  };

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_BASE}/history`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to load history");
        if (!cancelled) setItems(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) setError(err.message || "Failed to load history");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, []);

  const goToRecipe = (item) => {
    navigate(`/recipe/${encodeURIComponent(item.recipe_name)}`, {
      state: {
        recipe: {
          name: item.recipe_name,
          is_veg: item.is_veg,
          cooking_time_minutes: item.cooking_time_minutes,
          image_url: item.image_url,
        },
      },
    });
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "40px 24px 80px" }}>
      <div style={CARD}>
        <div style={{ height: 8 }} />
        <p style={{ color: "#6b7280", fontSize: "0.9rem", marginBottom: "16px" }}>
          View your past recipe generations and ingredient detections.
        </p>
      </div>

      {loading && (
        <div style={{ marginTop: 16, padding: "18px 20px", borderRadius: 16,
          background: "rgba(250,246,237,0.97)", color: "#6b7280" }}>
          Loading history...
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
          No history to show yet.
        </div>
      )}

      {!loading && !error && items.length > 0 && (
        <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 12 }}>
          {items.map((item, i) => (
            <motion.div key={item.id ?? `${item.recipe_name}-${i}`}
              initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              whileHover={{ x: 4 }} whileTap={{ scale: 0.99 }}
              onClick={() => goToRecipe(item)}
              style={{ padding: "14px 16px", borderRadius: 14, cursor: "pointer",
                background: "rgba(250,246,237,0.97)", border: "1px solid rgba(200,135,58,0.2)",
                transition: "all 0.2s", display: "flex", alignItems: "center", gap: 12 }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(250,246,237,1)";
                e.currentTarget.style.border = "1px solid rgba(200,135,58,0.45)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "rgba(250,246,237,0.97)";
                e.currentTarget.style.border = "1px solid rgba(200,135,58,0.2)";
              }}>
              <img
                src={item.image_url}
                alt={item.recipe_name}
                style={{ width: 56, height: 56, borderRadius: 12, objectFit: "cover", flexShrink: 0 }}
                loading="lazy"
              />
              <div style={{ flex: 1 }}>
                <h3 style={{ fontWeight: 700, color: "#2d2d2d", fontSize: "0.95rem", marginBottom: 6 }}>
                  {item.recipe_name}
                </h3>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {item.is_veg !== undefined && (
                    <span style={{ display: "flex", alignItems: "center", gap: 4,
                      padding: "3px 10px", borderRadius: 20, fontSize: "0.72rem", fontWeight: 600,
                      background: item.is_veg ? "rgba(74,158,107,0.12)" : "rgba(239,68,68,0.1)",
                      color: item.is_veg ? "#2d6a4a" : "#dc2626",
                      border: `1px solid ${item.is_veg ? "rgba(74,158,107,0.3)" : "rgba(239,68,68,0.25)"}` }}>
                      {item.is_veg ? <Leaf size={11} /> : <Flame size={11} />}
                      {item.is_veg ? "Veg" : "Non-Veg"}
                    </span>
                  )}
                  {item.cooking_time_minutes && (
                    <span style={{ display: "flex", alignItems: "center", gap: 4,
                      padding: "3px 10px", borderRadius: 20, fontSize: "0.72rem", fontWeight: 600,
                      background: "rgba(200,135,58,0.1)", color: "#C8873A",
                      border: "1px solid rgba(200,135,58,0.25)" }}>
                      <Clock size={11} /> {item.cooking_time_minutes} min
                    </span>
                  )}
                </div>
              </div>
              <ArrowRight size={17} style={{ color: "#C8873A", marginLeft: 10 }} />
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
