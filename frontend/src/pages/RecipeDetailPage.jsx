import { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft, Clock, Leaf, Flame, ChefHat, Send,
  Loader2, BookOpen, ShoppingBasket, MessageCircle, Sparkles,
} from "lucide-react";
import Navbar from "../components/Navbar";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const BG = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1920&q=80";

const FOOD_IMAGES = {
  chicken: "https://images.unsplash.com/photo-1598103442097-8b74394b95c3?w=800&q=80",
  curry:   "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=800&q=80",
  paneer:  "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=800&q=80",
  rice:    "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=800&q=80",
  tomato:  "https://images.unsplash.com/photo-1546470427-e26264be0b0d?w=800&q=80",
  egg:     "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=800&q=80",
  default: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
};

function getRecipeImage(name = "") {
  const lower = name.toLowerCase();
  for (const [key, url] of Object.entries(FOOD_IMAGES)) {
    if (lower.includes(key)) return url;
  }
  return FOOD_IMAGES.default;
}

export default function RecipeDetailPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { recipeName } = useParams();

  const recipe = location.state?.recipe || {};
  const detectedIngredients = location.state?.detectedIngredients || [];
  const name = recipe.name || decodeURIComponent(recipeName);

  const [instructions, setInstructions] = useState(null);
  const [loadingInstructions, setLoadingInstructions] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [prefs, setPrefs] = useState({ diet: "vegetarian", spice_level: "medium", cooking_time: "normal" });

  const [messages, setMessages] = useState([{
    role: "assistant",
    text: `Hi! I'm your cooking assistant for **${name}**. Ask me anything — substitutions, tips, spice adjustments, or any doubts! 🍳`,
  }]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const fetchInstructions = async () => {
    if (instructions) { setActiveTab("instructions"); return; }
    setLoadingInstructions(true);
    setActiveTab("instructions");
    try {
      const token = localStorage.getItem("token");
      const ingredients = recipe.matched_ingredients?.length
        ? recipe.matched_ingredients
        : detectedIngredients.length ? detectedIngredients : [name];
      const res = await fetch(`${API_BASE}/generate-instructions`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ ingredients, preferences: prefs }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed");
      setInstructions(data);
    } catch (err) { setInstructions({ error: err.message }); }
    finally { setLoadingInstructions(false); }
  };

  const sendChat = async () => {
    const text = chatInput.trim();
    if (!text || chatLoading) return;
    setChatInput("");
    setMessages((prev) => [...prev, { role: "user", text }]);
    setChatLoading(true);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_BASE}/generate-instructions`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          ingredients: detectedIngredients.length ? detectedIngredients : [name],
          preferences: { ...prefs },
        }),
      });
      const data = await res.json();
      const reply = data.instructions || data.message || data.recipe_instructions ||
        "Here's my tip: Prep all ingredients first, cook on medium heat, and adjust seasoning to taste!";
      setMessages((prev) => [...prev, { role: "assistant", text: typeof reply === "object" ? JSON.stringify(reply) : reply }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", text: "Sorry, couldn't connect. Try again!" }]);
    } finally { setChatLoading(false); }
  };

  const recipeIngredients = recipe.ingredients || recipe.matched_ingredients || detectedIngredients;
  const CARD = { background: "rgba(250,246,237,0.97)", borderRadius: 20, backdropFilter: "blur(8px)" };

  const TAB = (active) => ({
    padding: "10px 18px", borderRadius: "10px 10px 0 0", fontSize: "0.85rem", fontWeight: 600,
    border: "none", cursor: "pointer", fontFamily: "inherit", transition: "all 0.2s",
    background: active ? "rgba(250,246,237,0.97)" : "rgba(250,246,237,0.4)",
    color: active ? "#C8873A" : "#6b7280",
    borderBottom: active ? "2px solid #C8873A" : "2px solid transparent",
  });

  return (
    <div style={{ minHeight: "100vh", position: "relative" }}>
      <div style={{ position: "fixed", inset: 0,
        backgroundImage: `linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.6)), url('${BG}')`,
        backgroundSize: "cover", backgroundPosition: "center", zIndex: 0 }} />
      <div style={{ position: "relative", zIndex: 1 }}>
        <Navbar />
        <div style={{ maxWidth: 860, margin: "0 auto", padding: "40px 24px 80px" }}>

          <motion.button initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }}
            onClick={() => navigate(-1)}
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.82rem",
              color: "rgba(255,255,255,0.7)", background: "none", border: "none", cursor: "pointer", marginBottom: 24 }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "rgba(255,255,255,0.7)")}>
            <ArrowLeft size={15} /> Back
          </motion.button>

          {/* Hero */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            style={{ position: "relative", borderRadius: 24, overflow: "hidden", height: 260, marginBottom: 20 }}>
            <img src={getRecipeImage(name)} alt={name}
              style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            <div style={{ position: "absolute", inset: 0,
              background: "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 70%, transparent 100%)" }} />
            <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, padding: "20px 24px" }}>
              <h1 style={{ fontFamily: '"Playfair Display", Georgia, serif',
                fontSize: "2rem", fontWeight: 900, color: "#fff", marginBottom: 8 }}>
                {name}
              </h1>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {recipe.is_veg !== undefined && (
                  <span style={{ display: "flex", alignItems: "center", gap: 4,
                    padding: "4px 12px", borderRadius: 20, fontSize: "0.76rem", fontWeight: 600,
                    background: recipe.is_veg ? "rgba(74,158,107,0.85)" : "rgba(220,38,38,0.85)",
                    color: "#fff" }}>
                    {recipe.is_veg ? <Leaf size={12} /> : <Flame size={12} />}
                    {recipe.is_veg ? "Vegetarian" : "Non-Vegetarian"}
                  </span>
                )}
                {recipe.cooking_time_minutes && (
                  <span style={{ display: "flex", alignItems: "center", gap: 4,
                    padding: "4px 12px", borderRadius: 20, fontSize: "0.76rem", fontWeight: 600,
                    background: "rgba(200,135,58,0.85)", color: "#fff" }}>
                    <Clock size={12} /> {recipe.cooking_time_minutes} min
                  </span>
                )}
              </div>
            </div>
          </motion.div>

          {/* Tabs */}
          <div style={{ display: "flex", gap: 4, marginBottom: 0 }}>
            <button style={TAB(activeTab === "overview")} onClick={() => setActiveTab("overview")}>
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}><ShoppingBasket size={14} /> Overview</span>
            </button>
            <button style={TAB(activeTab === "instructions")} onClick={fetchInstructions}>
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}><BookOpen size={14} /> Instructions</span>
            </button>
            <button style={TAB(activeTab === "chat")} onClick={() => setActiveTab("chat")}>
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}><MessageCircle size={14} /> Ask AI Chef</span>
            </button>
          </div>

          {/* Tab content */}
          <div style={{ ...CARD, padding: 28, borderRadius: "0 16px 16px 16px", border: "1px solid rgba(200,135,58,0.2)" }}>
            <AnimatePresence mode="wait">

              {/* OVERVIEW */}
              {activeTab === "overview" && (
                <motion.div key="overview" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                  {/* Ingredients */}
                  <div style={{ marginBottom: 24 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                      <ShoppingBasket size={17} color="#4a9e6b" />
                      <h2 style={{ fontWeight: 700, color: "#2d2d2d", fontSize: "1rem", margin: 0 }}>Ingredients</h2>
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      {recipeIngredients.length > 0
                        ? recipeIngredients.map((ing, i) => (
                          <span key={i} style={{ padding: "7px 16px", borderRadius: 20,
                            fontSize: "0.85rem", fontWeight: 500,
                            background: "rgba(74,158,107,0.1)", color: "#2d6a4a",
                            border: "1px solid rgba(74,158,107,0.25)" }}>
                            {ing}
                          </span>
                        ))
                        : <p style={{ color: "#9ca3af", fontSize: "0.85rem" }}>No ingredient details available.</p>
                      }
                    </div>
                  </div>

                  {/* Preferences */}
                  <div style={{ padding: 20, borderRadius: 16,
                    background: "rgba(200,135,58,0.06)", border: "1px solid rgba(200,135,58,0.2)", marginBottom: 20 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                      <Sparkles size={17} color="#C8873A" />
                      <h2 style={{ fontWeight: 700, color: "#C8873A", fontSize: "1rem", margin: 0 }}>Cooking Preferences</h2>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12 }}>
                      {[
                        { label: "Diet", key: "diet", options: ["vegetarian", "non-vegetarian", "vegan"] },
                        { label: "Spice Level", key: "spice_level", options: ["mild", "medium", "spicy"] },
                        { label: "Cooking Time", key: "cooking_time", options: ["quick", "normal", "elaborate"] },
                      ].map(({ label, key, options }) => (
                        <div key={key}>
                          <p style={{ fontSize: "0.7rem", fontWeight: 700, color: "#9ca3af",
                            textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>
                            {label}
                          </p>
                          <select value={prefs[key]}
                            onChange={(e) => setPrefs((p) => ({ ...p, [key]: e.target.value }))}
                            style={{ width: "100%", padding: "8px 12px", borderRadius: 10,
                              background: "#fff", border: "1.5px solid rgba(200,135,58,0.3)",
                              color: "#2d2d2d", fontSize: "0.85rem", fontFamily: "inherit" }}>
                            {options.map((o) => <option key={o} value={o}>{o}</option>)}
                          </select>
                        </div>
                      ))}
                    </div>
                  </div>

                  <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                    onClick={fetchInstructions}
                    style={{ width: "100%", padding: "14px", borderRadius: 14, border: "none",
                      background: "#C8873A", color: "#fff", fontSize: "1rem", fontWeight: 700,
                      cursor: "pointer", fontFamily: "inherit",
                      display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
                    <BookOpen size={17} /> Generate Step-by-Step Instructions
                  </motion.button>
                </motion.div>
              )}

              {/* INSTRUCTIONS */}
              {activeTab === "instructions" && (
                <motion.div key="instructions" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                  {loadingInstructions ? (
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "48px 0", gap: 14 }}>
                      <Loader2 size={32} color="#C8873A" style={{ animation: "spin 1s linear infinite" }} />
                      <p style={{ color: "#6b7280" }}>Generating instructions...</p>
                    </div>
                  ) : instructions?.error ? (
                    <div style={{ padding: "14px 18px", borderRadius: 12,
                      background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)",
                      color: "#dc2626", fontSize: "0.85rem" }}>
                      {instructions.error}
                    </div>
                  ) : instructions ? (() => {
                    const content = instructions.instructions || instructions.recipe_instructions ||
                      instructions.steps || instructions.message || instructions;
                    const lines = typeof content === "string"
                      ? content.split(/\n+/).filter(Boolean)
                      : Array.isArray(content) ? content : [JSON.stringify(content)];
                    return (
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
                          <BookOpen size={17} color="#C8873A" />
                          <h2 style={{ fontWeight: 700, color: "#C8873A", fontSize: "1rem", margin: 0 }}>
                            Step-by-Step Instructions
                          </h2>
                        </div>
                        {lines.map((line, i) => (
                          <motion.div key={i}
                            initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.04 }}
                            style={{ display: "flex", gap: 14, marginBottom: 16, alignItems: "flex-start" }}>
                            <div style={{ width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
                              background: "rgba(200,135,58,0.15)", border: "1px solid rgba(200,135,58,0.35)",
                              display: "flex", alignItems: "center", justifyContent: "center",
                              fontSize: "0.75rem", fontWeight: 700, color: "#C8873A" }}>
                              {i + 1}
                            </div>
                            <p className="selectable-text"
                              style={{ color: "#374151", fontSize: "0.9rem", lineHeight: 1.7, paddingTop: 4, margin: 0 }}>
                              {typeof line === "object" ? line.step || line.instruction || JSON.stringify(line) : line}
                            </p>
                          </motion.div>
                        ))}
                        <button onClick={() => setActiveTab("chat")}
                          style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 8,
                            padding: "9px 18px", borderRadius: 10,
                            border: "1px solid rgba(74,158,107,0.35)",
                            background: "rgba(74,158,107,0.08)", color: "#2d6a4a",
                            fontSize: "0.85rem", fontWeight: 600, cursor: "pointer", fontFamily: "inherit" }}>
                          <MessageCircle size={14} /> Have questions? Ask AI Chef
                        </button>
                      </div>
                    );
                  })() : (
                    <p style={{ color: "#9ca3af", textAlign: "center", padding: "32px 0" }}>
                      Click "Generate Instructions" to get started.
                    </p>
                  )}
                </motion.div>
              )}

              {/* CHAT */}
              {activeTab === "chat" && (
                <motion.div key="chat" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                  <div style={{ border: "1px solid rgba(200,135,58,0.2)", borderRadius: 16, overflow: "hidden" }}>
                    {/* Chat header */}
                    <div style={{ padding: "14px 18px", background: "rgba(200,135,58,0.06)",
                      borderBottom: "1px solid rgba(200,135,58,0.15)",
                      display: "flex", alignItems: "center", gap: 10 }}>
                      <div style={{ width: 34, height: 34, borderRadius: "50%",
                        background: "rgba(200,135,58,0.15)", border: "1px solid rgba(200,135,58,0.3)",
                        display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <ChefHat size={17} color="#C8873A" />
                      </div>
                      <div>
                        <p style={{ fontWeight: 700, color: "#C8873A", fontSize: "0.88rem", margin: 0 }}>AI Chef Assistant</p>
                        <p style={{ fontSize: "0.7rem", color: "#9ca3af", margin: 0 }}>Ask anything about {name}</p>
                      </div>
                      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 6 }}>
                        <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#4a9e6b" }} />
                        <span style={{ fontSize: "0.7rem", color: "#4a9e6b", fontWeight: 600 }}>Online</span>
                      </div>
                    </div>

                    {/* Messages */}
                    <div style={{ height: 360, overflowY: "auto", padding: "18px 18px 8px",
                      display: "flex", flexDirection: "column", gap: 12,
                      background: "#fdfaf5" }}>
                      {messages.map((msg, i) => (
                        <motion.div key={i} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
                          style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start" }}>
                          {msg.role === "assistant" && (
                            <div style={{ width: 26, height: 26, borderRadius: "50%", flexShrink: 0,
                              background: "rgba(200,135,58,0.15)", display: "flex", alignItems: "center",
                              justifyContent: "center", marginRight: 8, alignSelf: "flex-end" }}>
                              <ChefHat size={13} color="#C8873A" />
                            </div>
                          )}
                          <div style={{
                            maxWidth: "75%", padding: "10px 14px", borderRadius: 16,
                            fontSize: "0.86rem", lineHeight: 1.6,
                            background: msg.role === "user" ? "#C8873A" : "#fff",
                            color: msg.role === "user" ? "#fff" : "#374151",
                            border: msg.role === "user" ? "none" : "1px solid rgba(0,0,0,0.08)",
                            borderBottomRightRadius: msg.role === "user" ? 4 : 16,
                            borderBottomLeftRadius: msg.role === "assistant" ? 4 : 16,
                            boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
                          }}>
                            {msg.text}
                          </div>
                        </motion.div>
                      ))}
                      {chatLoading && (
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <div style={{ width: 26, height: 26, borderRadius: "50%",
                            background: "rgba(200,135,58,0.15)", display: "flex",
                            alignItems: "center", justifyContent: "center" }}>
                            <ChefHat size={13} color="#C8873A" />
                          </div>
                          <div style={{ padding: "10px 14px", borderRadius: 16, background: "#fff",
                            border: "1px solid rgba(0,0,0,0.08)" }}>
                            <div style={{ display: "flex", gap: 4 }}>
                              {[0,1,2].map((j) => (
                                <div key={j} style={{ width: 6, height: 6, borderRadius: "50%",
                                  background: "#C8873A", opacity: 0.5,
                                  animation: `bounce 1.2s ease-in-out ${j * 0.2}s infinite` }} />
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                      <div ref={chatEndRef} />
                    </div>

                    {/* Suggested questions */}
                    <div style={{ padding: "8px 16px", display: "flex", gap: 8, flexWrap: "wrap",
                      background: "#fdfaf5", borderTop: "1px solid rgba(0,0,0,0.06)" }}>
                      {["Can I substitute any ingredient?", "How to reduce spice?", "Can I meal prep this?"].map((q) => (
                        <button key={q} onClick={() => setChatInput(q)}
                          style={{ padding: "5px 12px", borderRadius: 20, fontSize: "0.72rem",
                            background: "rgba(200,135,58,0.08)", color: "#7c4a10",
                            border: "1px solid rgba(200,135,58,0.25)", cursor: "pointer", fontFamily: "inherit" }}>
                          {q}
                        </button>
                      ))}
                    </div>

                    {/* Input */}
                    <div style={{ padding: "12px 14px", borderTop: "1px solid rgba(0,0,0,0.08)",
                      display: "flex", gap: 10, background: "#fff" }}>
                      <input type="text" value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && sendChat()}
                        placeholder={`Ask about ${name}...`}
                        style={{ flex: 1, padding: "10px 14px", borderRadius: 12,
                          background: "#fdfaf5", border: "1.5px solid rgba(200,135,58,0.3)",
                          color: "#2d2d2d", fontSize: "0.87rem", outline: "none", fontFamily: "inherit" }}
                        onFocus={(e) => {
                          e.target.style.border = "1.5px solid #C8873A";
                          e.target.style.boxShadow = "0 0 0 3px rgba(200,135,58,0.1)";
                        }}
                        onBlur={(e) => {
                          e.target.style.border = "1.5px solid rgba(200,135,58,0.3)";
                          e.target.style.boxShadow = "none";
                        }} />
                      <motion.button whileHover={{ scale: 1.06 }} whileTap={{ scale: 0.94 }}
                        onClick={sendChat} disabled={!chatInput.trim() || chatLoading}
                        style={{ width: 42, height: 42, borderRadius: 12, border: "none",
                          background: chatInput.trim() ? "#C8873A" : "rgba(200,135,58,0.15)",
                          color: chatInput.trim() ? "#fff" : "#9ca3af",
                          cursor: chatInput.trim() ? "pointer" : "not-allowed",
                          display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <Send size={16} />
                      </motion.button>
                    </div>
                  </div>
                  <style>{`
                    @keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-5px)} }
                    @keyframes spin { to{transform:rotate(360deg)} }
                  `}</style>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}