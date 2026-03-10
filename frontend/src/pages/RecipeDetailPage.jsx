import { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft, Clock, Leaf, Flame, ChefHat, Send,
  Loader2, BookOpen, ShoppingBasket, MessageCircle, Sparkles, Heart,
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const FALLBACK_IMAGE = "https://source.unsplash.com/1200x600/?food";

function getRecipeImage(name = "") {
  const query = encodeURIComponent(String(name || "recipe"));
  return `https://source.unsplash.com/1200x600/?food,${query}`;
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
  const [prefs, setPrefs] = useState({ spice_level: "medium", cooking_time: "normal" });
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [wishlistLoading, setWishlistLoading] = useState(false);
  const [cooldownUntil, setCooldownUntil] = useState(null);

  const [messages, setMessages] = useState([{
    role: "assistant",
    text: `Hi! I'm your cooking assistant for **${name}**. Ask me anything — substitutions, tips, spice adjustments, or any doubts! 🍳`,
  }]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef(null);
  const hasMountedRef = useRef(false);
  const pendingScrollRef = useRef(0);

  const appendMessage = (msg) => {
    pendingScrollRef.current += 1;
    setMessages((prev) => [...prev, msg]);
  };

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "auto" });
  }, []);

  useEffect(() => {
    if (!hasMountedRef.current) {
      hasMountedRef.current = true;
      return;
    }
    if (pendingScrollRef.current > 0) {
      pendingScrollRef.current -= 1;
      chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  useEffect(() => {
    let cancelled = false;
    const loadWishlist = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;
        const res = await fetch(`${API_BASE}/wishlist`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) return;
        const data = await res.json();
        if (cancelled) return;
        const normalizedName = (name || "").toLowerCase();
        const match = (Array.isArray(data) ? data : []).find((item) => (
          (recipe.id && item.id === recipe.id) ||
          (!recipe.id && item.name && item.name.toLowerCase() === normalizedName)
        ));
        setIsWishlisted(Boolean(match));
      } catch {
        if (!cancelled) setIsWishlisted(false);
      }
    };
    loadWishlist();
    return () => { cancelled = true; };
  }, [recipe.id, name]);

  useEffect(() => {
    const recordHistory = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;
        const body = recipe.id ? { recipe_id: recipe.id } : { recipe_name: name };
        await fetch(`${API_BASE}/history`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
      } catch {
        // ignore history errors
      }
    };
    recordHistory();
  }, [recipe.id, name]);

  const addToWishlist = async () => {
    if (wishlistLoading || isWishlisted) return;
    setWishlistLoading(true);
    try {
      const token = localStorage.getItem("token");
      const body = recipe.id ? { recipe_id: recipe.id } : { recipe_name: name };
      const res = await fetch(`${API_BASE}/wishlist`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to add to wishlist");
      }
      setIsWishlisted(true);
    } catch (err) {
      alert(err.message || "Failed to add to wishlist");
    } finally {
      setWishlistLoading(false);
    }
  };

  const fetchInstructions = async () => {
    if (instructions || loadingInstructions) { return; }
    if (cooldownUntil && Date.now() < cooldownUntil) { return; }
    setLoadingInstructions(true);
    try {
      const token = localStorage.getItem("token");
      const ingredients = recipe.matched_ingredients?.length
        ? recipe.matched_ingredients
        : detectedIngredients.length ? detectedIngredients : [name];
      const res = await fetch(`${API_BASE}/generate-instructions`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ ingredients, preferences: prefs, recipe_name: name }),
      });
      const data = await res.json();
      if (!res.ok) {
        if (res.status === 429) {
          setCooldownUntil(Date.now() + 60 * 1000);
        }
        throw new Error(data.detail || "Failed");
      }
      setInstructions(data);
    } catch (err) { setInstructions({ error: err.message }); }
    finally { setLoadingInstructions(false); }
  };

  const sendChat = async () => {
    const text = chatInput.trim();
    if (!text || chatLoading) return;
    if (cooldownUntil && Date.now() < cooldownUntil) {
      appendMessage({ role: "assistant", text: "Gemini is busy. Please wait a minute and try again." });
      return;
    }
    setChatInput("");
    appendMessage({ role: "user", text });
    setChatLoading(true);
    try {
      const token = localStorage.getItem("token");
      const messagesPayload = [
        ...messages.map((m) => ({ role: m.role, content: m.text })),
        { role: "user", content: text },
      ];
      const res = await fetch(`${API_BASE}/gemini-chat`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: messagesPayload,
          ingredients: detectedIngredients.length ? detectedIngredients : [name],
          recipe_name: name,
          preferences: { ...prefs },
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        if (res.status === 429) {
          setCooldownUntil(Date.now() + 60 * 1000);
        }
        throw new Error("Assistant temporarily unavailable. Please try again.");
      }
      const reply = data.reply || data.message ||
        "Here's my tip: Prep all ingredients first, cook on medium heat, and adjust seasoning to taste!";
      appendMessage({ role: "assistant", text: typeof reply === "object" ? JSON.stringify(reply) : reply });
    } catch (err) {
      appendMessage({ role: "assistant", text: "Assistant temporarily unavailable. Please try again." });
    } finally { setChatLoading(false); }
  };

  const recipeIngredients = recipe.ingredients || recipe.matched_ingredients || detectedIngredients;
  const heroImage = getRecipeImage(name);
  const heroFallback = FALLBACK_IMAGE;
  const [heroSrc, setHeroSrc] = useState(heroImage);

  useEffect(() => {
    setHeroSrc(heroImage);
  }, [heroImage]);
  const CARD = { background: "rgba(250,246,237,0.97)", borderRadius: 20, backdropFilter: "blur(8px)" };

  const TAB = (active) => ({
    padding: "10px 18px", borderRadius: "10px 10px 0 0", fontSize: "0.85rem", fontWeight: 600,
    border: "none", cursor: "pointer", fontFamily: "inherit", transition: "all 0.2s",
    background: active ? "rgba(250,246,237,0.97)" : "rgba(250,246,237,0.4)",
    color: active ? "#C8873A" : "#6b7280",
    borderBottom: active ? "2px solid #C8873A" : "2px solid transparent",
  });

  return (
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
            style={{
              position: "relative",
              borderRadius: 24,
              overflow: "hidden",
              height: 260,
              marginBottom: 20,
              backgroundImage: `url('${heroSrc}')`,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}>
            <img src={heroSrc} alt={name}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
              onError={() => setHeroSrc(heroFallback)} />
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
          <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 10 }}>
            <button
              onClick={addToWishlist}
              disabled={wishlistLoading || isWishlisted}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "8px 14px",
                borderRadius: 999,
                border: "1px solid rgba(200,135,58,0.35)",
                background: "#ffffff",
                color: "#000000",
                fontSize: "0.82rem",
                fontWeight: 700,
                cursor: wishlistLoading || isWishlisted ? "not-allowed" : "pointer",
                fontFamily: "inherit",
              }}
            >
              <Heart size={14} />
              {isWishlisted ? "In Wishlist" : wishlistLoading ? "Adding..." : "Add to Wishlist"}
            </button>
          </div>
          <div style={{ display: "flex", gap: 4, marginBottom: 0 }}>
            <button style={TAB(activeTab === "overview")} onClick={() => setActiveTab("overview")}>
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}><ShoppingBasket size={14} /> Overview</span>
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
                    disabled={loadingInstructions || (cooldownUntil && Date.now() < cooldownUntil)}
                    style={{ width: "100%", padding: "14px", borderRadius: 14, border: "none",
                      background: "#C8873A", color: "#fff", fontSize: "1rem", fontWeight: 700,
                      cursor: "pointer", fontFamily: "inherit",
                      display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
                    <BookOpen size={17} /> Generate Step-by-Step Instructions
                  </motion.button>

                  <div style={{ marginTop: 20 }}>
                    {loadingInstructions ? (
                      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "32px 0", gap: 14 }}>
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
                          <div style={{ height: 8 }} />
                        </div>
                      );
                    })() : null}
                  </div>

                  {/* Chat Assistant */}
                  <div style={{ marginTop: 24 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                      <MessageCircle size={16} color="#C8873A" />
                      <h3 style={{ fontWeight: 700, color: "#C8873A", fontSize: "1rem", margin: 0 }}>
                        Chat Assistant
                      </h3>
                    </div>
                    <p style={{ color: "#6b7280", fontSize: "0.85rem", marginTop: 0, marginBottom: 12 }}>
                      Let me help you prepare this curry.
                    </p>

                    <div style={{
                      background: "#f7f2ea",
                      borderRadius: 16,
                      boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
                      border: "1px solid rgba(200,135,58,0.2)",
                      overflow: "hidden"
                    }}>
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
                          <p style={{ fontWeight: 700, color: "#C8873A", fontSize: "0.88rem", margin: 0 }}>Chat Assistant</p>
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
                  </div>
                </motion.div>
              )}

            </AnimatePresence>
          </div>
      </div>
  );
}
