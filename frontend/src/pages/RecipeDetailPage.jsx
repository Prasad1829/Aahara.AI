import { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft, Clock, Leaf, Flame, ChefHat, Send,
  BookOpen, ShoppingBasket, MessageCircle, Sparkles, Heart,
} from "lucide-react";
import RecipeImage from "../components/RecipeImage";
import RecipeGenerationLoader from "../components/RecipeGenerationLoader";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function RecipeDetailPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { recipeName } = useParams();

  const recipe = location.state?.recipe || {};
  const detectedIngredients = location.state?.detectedIngredients || [];
  const name = recipe.name || decodeURIComponent(recipeName);
  const recipeIngredients = recipe.ingredients || recipe.matched_ingredients || detectedIngredients;
  const inferredDiet = recipe.is_veg === undefined
    ? "auto"
    : (recipe.is_veg ? "vegetarian" : "non-vegetarian");

  const [instructions, setInstructions] = useState(null);
  const [loadingInstructions, setLoadingInstructions] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [prefs, setPrefs] = useState({ spice_level: "medium", cooking_time: "normal" });
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [wishlistRecipeId, setWishlistRecipeId] = useState(null);
  const [wishlistLoading, setWishlistLoading] = useState(false);
  const [cooldownUntil, setCooldownUntil] = useState(null);

  const [messages, setMessages] = useState([{
    role: "assistant",
    text: `Hi! I'm your cooking assistant for **${name}**. Ask me anything — substitutions, tips, spice adjustments, or any doubts! 🍳`,
  }]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatScrollRef = useRef(null);
  const hasMountedRef = useRef(false);
  const pendingScrollRef = useRef(0);

  const appendMessage = (msg) => {
    pendingScrollRef.current += 1;
    setMessages((prev) => [...prev, msg]);
  };

  useEffect(() => {
    setInstructions(null);
    setChatInput("");
    setCooldownUntil(null);
    setMessages([{
      role: "assistant",
      text: `Hi! I'm your cooking assistant for **${name}**. Ask me anything about this recipe - ingredients, steps, substitutions, spice adjustments, or meal prep tips.`,
    }]);
  }, [name]);

  useEffect(() => { window.scrollTo({ top: 0, behavior: "auto" }); }, []);

  useEffect(() => {
    if (!hasMountedRef.current) { hasMountedRef.current = true; return; }
    if (pendingScrollRef.current > 0) {
      pendingScrollRef.current -= 1;
      chatScrollRef.current?.scrollTo({
        top: chatScrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  useEffect(() => {
    let cancelled = false;
    const loadWishlist = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;
        const res = await fetch(`${API_BASE}/wishlist`, { headers: { Authorization: `Bearer ${token}` } });
        if (!res.ok) return;
        const data = await res.json();
        if (cancelled) return;
        const normalizedName = (name || "").toLowerCase();
        const match = (Array.isArray(data) ? data : []).find((item) => (
          (recipe.id && item.id === recipe.id) ||
          (!recipe.id && item.name && item.name.toLowerCase() === normalizedName)
        ));
        setIsWishlisted(Boolean(match));
        setWishlistRecipeId(match?.id ?? recipe.id ?? null);
      } catch {
        if (!cancelled) {
          setIsWishlisted(false);
          setWishlistRecipeId(null);
        }
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
      } catch {}
    };
    recordHistory();
  }, [recipe.id, name]);

  const toggleWishlist = async () => {
    if (wishlistLoading) return;
    setWishlistLoading(true);
    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("Please login first.");

      if (isWishlisted) {
        const recipeIdToRemove = wishlistRecipeId ?? recipe.id ?? null;
        if (!recipeIdToRemove) {
          throw new Error("Unable to remove this recipe from wishlist right now.");
        }

        const res = await fetch(`${API_BASE}/wishlist/${recipeIdToRemove}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || "Failed");
        }
        setIsWishlisted(false);
        setWishlistRecipeId(null);
      } else {
        const body = recipe.id ? { recipe_id: recipe.id } : { recipe_name: name };
        const res = await fetch(`${API_BASE}/wishlist`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || "Failed");
        }
        setIsWishlisted(true);
        setWishlistRecipeId(data.id ?? recipe.id ?? null);
      }
    } catch (err) {
      alert(err.message || "Failed to update wishlist");
    }
    finally { setWishlistLoading(false); }
  };

  const fetchInstructions = async () => {
    if (instructions || loadingInstructions) return;
    if (cooldownUntil && Date.now() < cooldownUntil) return;
    setLoadingInstructions(true);
    try {
      const token = localStorage.getItem("token");
      const ingredients = recipeIngredients.length ? recipeIngredients : [name];
      const res = await fetch(`${API_BASE}/generate-instructions`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ ingredients, preferences: { ...prefs, diet: inferredDiet }, recipe_name: name }),
      });
      const data = await res.json();
      if (!res.ok) { if (res.status === 429) setCooldownUntil(Date.now() + 60 * 1000); throw new Error(data.detail || "Failed"); }
      setInstructions(data);
    } catch (err) { setInstructions({ error: err.message }); }
    finally { setLoadingInstructions(false); }
  };

  const sendChat = async () => {
    const text = chatInput.trim();
    if (!text || chatLoading) return;
    if (cooldownUntil && Date.now() < cooldownUntil) {
      appendMessage({ role: "assistant", text: "Please wait a minute and try again." });
      return;
    }
    setChatInput("");
    appendMessage({ role: "user", text });
    setChatLoading(true);
    try {
      const token = localStorage.getItem("token");
      const messagesPayload = [
        ...messages.slice(-6).map((m) => ({ role: m.role, content: m.text })),
        { role: "user", content: text },
      ];
      const res = await fetch(`${API_BASE}/gemini-chat`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: messagesPayload,
          ingredients: recipeIngredients.length ? recipeIngredients : [name],
          recipe_name: name,
          preferences: { ...prefs, diet: inferredDiet },
        }),
      });
      const data = await res.json();
      if (!res.ok) { if (res.status === 429) setCooldownUntil(Date.now() + 60 * 1000); throw new Error("Unavailable"); }
      const reply = data.reply || data.message || "Here's my tip: Prep all ingredients first, cook on medium heat!";
      appendMessage({ role: "assistant", text: typeof reply === "object" ? JSON.stringify(reply) : reply });
    } catch { appendMessage({ role: "assistant", text: "Assistant temporarily unavailable. Please try again." }); }
    finally { setChatLoading(false); }
  };

  const CARD = { background: "rgba(250,246,237,0.97)", borderRadius: 20, backdropFilter: "blur(8px)" };

  const TAB = (active) => ({
    padding: "10px 18px", borderRadius: "10px 10px 0 0", fontSize: "0.85rem", fontWeight: 600,
    border: "none", cursor: "pointer", fontFamily: "inherit", transition: "all 0.2s",
    background: active ? "rgba(250,246,237,0.97)" : "rgba(250,246,237,0.4)",
    color: active ? "#C8873A" : "#6b7280",
    borderBottom: active ? "2px solid #C8873A" : "2px solid transparent",
  });

  return (
    <div style={{ maxWidth: 860, margin: "0 auto", padding: "24px 24px 80px" }}>

      <motion.button initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }}
        onClick={() => {
          const returnTo = location.state?.returnTo;
          if (returnTo?.path) {
            navigate(returnTo.path, { replace: true, state: { restoreState: returnTo.state } });
            return;
          }
          navigate(-1);
        }}
        style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.82rem",
          color: "#ffffff", background: "rgba(255,255,255,0.15)", border: "1px solid rgba(255,255,255,0.3)",
          borderRadius: 8, padding: "6px 12px", cursor: "pointer", marginBottom: 20 }}
        onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.25)")}
        onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.15)")}>
        <ArrowLeft size={15} /> Back
      </motion.button>

      <div style={{ display: "flex", gap: 4, marginBottom: 0 }}>
        <button style={TAB(activeTab === "overview")} onClick={() => setActiveTab("overview")}>
          <span style={{ display: "flex", alignItems: "center", gap: 6 }}><ShoppingBasket size={14} /> Overview</span>
        </button>
      </div>

      <div style={{ ...CARD, padding: 24, borderRadius: "0 16px 16px 16px", border: "1px solid rgba(200,135,58,0.2)" }}>
        <AnimatePresence mode="wait">
          {activeTab === "overview" && (
            <motion.div key="overview" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>

              <div style={{ display: "flex", gap: 20, marginBottom: 24, alignItems: "flex-start" }}>
                <div style={{ width: 140, height: 140, flexShrink: 0 }}>
                  <RecipeImage
                    name={name}
                    ingredients={recipeIngredients}
                    imageUrl={recipe.image_url}
                    imageFallbackUrl={recipe.image_fallback_url}
                    alt={name}
                    style={{ width: 140, height: 140, borderRadius: 16, objectFit: "cover",
                      border: "1px solid rgba(200,135,58,0.2)" }}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                    <h1 style={{ fontFamily: '"Playfair Display", Georgia, serif',
                      fontSize: "1.6rem", fontWeight: 900, color: "#2d2d2d", margin: 0 }}>
                      {name}
                    </h1>
                    <button
                      onClick={toggleWishlist}
                      disabled={wishlistLoading}
                      aria-label={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
                      title={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
                      style={{
                        width: 34,
                        height: 34,
                        borderRadius: "50%",
                        border: "1px solid rgba(200,135,58,0.22)",
                        background: isWishlisted ? "rgba(220,38,38,0.08)" : "#fff",
                        color: isWishlisted ? "#dc2626" : "#7c4a10",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        cursor: wishlistLoading ? "not-allowed" : "pointer",
                        flexShrink: 0,
                        padding: 0,
                      }}>
                      <Heart
                        size={16}
                        color={isWishlisted ? "#dc2626" : "#7c4a10"}
                        fill={isWishlisted ? "#dc2626" : "transparent"}
                      />
                    </button>
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 14 }}>
                    {recipe.is_veg !== undefined && (
                      <span style={{ display: "flex", alignItems: "center", gap: 4,
                        padding: "4px 12px", borderRadius: 20, fontSize: "0.76rem", fontWeight: 600,
                        background: recipe.is_veg ? "rgba(74,158,107,0.15)" : "rgba(220,38,38,0.1)",
                        color: recipe.is_veg ? "#2d6a4a" : "#dc2626",
                        border: `1px solid ${recipe.is_veg ? "rgba(74,158,107,0.3)" : "rgba(220,38,38,0.25)"}` }}>
                        {recipe.is_veg ? <Leaf size={12} /> : <Flame size={12} />}
                        {recipe.is_veg ? "Vegetarian" : "Non-Vegetarian"}
                      </span>
                    )}
                    {recipe.cooking_time_minutes && (
                      <span style={{ display: "flex", alignItems: "center", gap: 4,
                        padding: "4px 12px", borderRadius: 20, fontSize: "0.76rem", fontWeight: 600,
                        background: "rgba(200,135,58,0.1)", color: "#C8873A",
                        border: "1px solid rgba(200,135,58,0.25)" }}>
                        <Clock size={12} /> {recipe.cooking_time_minutes} min
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div style={{ marginBottom: 20 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                  <ShoppingBasket size={16} color="#4a9e6b" />
                  <h2 style={{ fontWeight: 700, color: "#2d2d2d", fontSize: "0.95rem", margin: 0 }}>Ingredients</h2>
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
                  {recipeIngredients.length > 0
                    ? recipeIngredients.map((ing, i) => (
                      <span key={i} style={{ padding: "6px 14px", borderRadius: 20,
                        fontSize: "0.82rem", fontWeight: 500,
                        background: "rgba(74,158,107,0.1)", color: "#2d6a4a",
                        border: "1px solid rgba(74,158,107,0.25)" }}>
                        {ing}
                      </span>
                    ))
                    : <p style={{ color: "#9ca3af", fontSize: "0.82rem" }}>No ingredient details available.</p>
                  }
                </div>
              </div>

              <div style={{ padding: 18, borderRadius: 14,
                background: "rgba(200,135,58,0.06)", border: "1px solid rgba(200,135,58,0.2)", marginBottom: 18 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                  <Sparkles size={16} color="#C8873A" />
                  <h2 style={{ fontWeight: 700, color: "#C8873A", fontSize: "0.95rem", margin: 0 }}>Cooking Preferences</h2>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 12 }}>
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
                style={{ width: "100%", padding: "13px", borderRadius: 14, border: "none",
                  background: "#C8873A", color: "#fff", fontSize: "0.95rem", fontWeight: 700,
                  cursor: "pointer", fontFamily: "inherit",
                  display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
                <BookOpen size={16} /> Generate Step-by-Step Instructions
              </motion.button>

              <div style={{ marginTop: 18 }}>
                {loadingInstructions ? (
                  <RecipeGenerationLoader
                    compact
                    accent="#C8873A"
                    title="Generating step-by-step instructions"
                    description="We're building a clear cooking flow for this recipe and your selected preferences."
                    steps={[
                      { label: "Planning the flow", Icon: BookOpen },
                      { label: "Adjusting for preferences", Icon: Sparkles },
                      { label: "Writing each step", Icon: ChefHat },
                    ]}
                  />
                ) : instructions?.error ? (
                  <div style={{ padding: "12px 16px", borderRadius: 12,
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
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
                        <BookOpen size={16} color="#C8873A" />
                        <h2 style={{ fontWeight: 700, color: "#C8873A", fontSize: "0.95rem", margin: 0 }}>
                          Step-by-Step Instructions
                        </h2>
                      </div>
                      {lines.map((line, i) => (
                        <motion.div key={i}
                          initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.04 }}
                          style={{ display: "flex", gap: 12, marginBottom: 14, alignItems: "flex-start" }}>
                          <div style={{ width: 26, height: 26, borderRadius: "50%", flexShrink: 0,
                            background: "rgba(200,135,58,0.15)", border: "1px solid rgba(200,135,58,0.35)",
                            display: "flex", alignItems: "center", justifyContent: "center",
                            fontSize: "0.72rem", fontWeight: 700, color: "#C8873A" }}>
                            {i + 1}
                          </div>
                          <p style={{ color: "#374151", fontSize: "0.88rem", lineHeight: 1.7, paddingTop: 3, margin: 0 }}>
                            {typeof line === "object" ? line.step || line.instruction || JSON.stringify(line) : line}
                          </p>
                        </motion.div>
                      ))}
                    </div>
                  );
                })() : null}
              </div>

              <div style={{ marginTop: 22 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                  <MessageCircle size={16} color="#C8873A" />
                  <h3 style={{ fontWeight: 700, color: "#C8873A", fontSize: "0.95rem", margin: 0 }}>Chat Assistant</h3>
                </div>
                <p style={{ color: "#6b7280", fontSize: "0.82rem", marginTop: 0, marginBottom: 10 }}>
                  Let me help you prepare this recipe.
                </p>

                <div style={{ background: "#f7f2ea", borderRadius: 16,
                  boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
                   border: "1px solid rgba(200,135,58,0.2)", overflow: "hidden" }}>
                  <div style={{ padding: "12px 16px", background: "rgba(200,135,58,0.06)",
                    borderBottom: "1px solid rgba(200,135,58,0.15)",
                    display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{ width: 32, height: 32, borderRadius: "50%",
                      background: "rgba(200,135,58,0.15)", border: "1px solid rgba(200,135,58,0.3)",
                      display: "flex", alignItems: "center", justifyContent: "center" }}>
                      <ChefHat size={16} color="#C8873A" />
                    </div>
                    <div>
                      <p style={{ fontWeight: 700, color: "#C8873A", fontSize: "0.85rem", margin: 0 }}>Chat Assistant</p>
                      <p style={{ fontSize: "0.68rem", color: "#9ca3af", margin: 0 }}>Ask anything about {name}</p>
                    </div>
                    <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 6 }}>
                       <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#4a9e6b" }} />
                      <span style={{ fontSize: "0.68rem", color: "#4a9e6b", fontWeight: 600 }}>Online</span>
                    </div>
                  </div>

                  <div ref={chatScrollRef} style={{ minHeight: 120, maxHeight: 320, overflowY: "auto", padding: "16px 16px 8px",
                    display: "flex", flexDirection: "column", gap: 10, background: "#fdfaf5" }}>
                    {messages.map((msg, i) => (
                      <motion.div key={i} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
                        style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start" }}>
                        {msg.role === "assistant" && (
                          <div style={{ width: 24, height: 24, borderRadius: "50%", flexShrink: 0,
                            background: "rgba(200,135,58,0.15)", display: "flex", alignItems: "center",
                            justifyContent: "center", marginRight: 8, alignSelf: "flex-end" }}>
                            <ChefHat size={12} color="#C8873A" />
                          </div>
                        )}
                        <div style={{ maxWidth: "75%", padding: "9px 13px", borderRadius: 14,
                          fontSize: "0.84rem", lineHeight: 1.6,
                          background: msg.role === "user" ? "#C8873A" : "#fff",
                          color: msg.role === "user" ? "#fff" : "#374151",
                          border: msg.role === "user" ? "none" : "1px solid rgba(0,0,0,0.08)",
                          borderBottomRightRadius: msg.role === "user" ? 4 : 14,
                          borderBottomLeftRadius: msg.role === "assistant" ? 4 : 14,
                          boxShadow: "0 1px 4px rgba(0,0,0,0.06)" }}>
                          {msg.text}
                        </div>
                      </motion.div>
                    ))}
                    {chatLoading && (
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <div style={{ width: 24, height: 24, borderRadius: "50%",
                          background: "rgba(200,135,58,0.15)", display: "flex",
                          alignItems: "center", justifyContent: "center" }}>
                          <ChefHat size={12} color="#C8873A" />
                        </div>
                        <div style={{ padding: "9px 13px", borderRadius: 14, background: "#fff",
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
                  </div>

                  <div style={{ padding: "8px 14px", display: "flex", gap: 7, flexWrap: "wrap",
                    background: "#fdfaf5", borderTop: "1px solid rgba(0,0,0,0.06)" }}>
                    {["Can I substitute any ingredient?", "How to reduce spice?", "Can I meal prep this?"].map((q) => (
                      <button key={q} onClick={() => setChatInput(q)}
                        style={{ padding: "4px 10px", borderRadius: 20, fontSize: "0.7rem",
                          background: "rgba(46,139,87,0.08)", color: "#2E8B57",
                          border: "1px solid rgba(208, 156, 34, 0.25)", cursor: "pointer", fontFamily: "inherit" }}>
                        {q}
                      </button>
                    ))}
                  </div>

                  <div style={{ padding: "10px 12px", borderTop: "1px solid rgba(0,0,0,0.08)",
                    display: "flex", gap: 8, background: "#fff" }}>
                    <input type="text" value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && sendChat()}
                      placeholder={`Ask about ${name}...`}
                      style={{ flex: 1, padding: "9px 13px", borderRadius: 10,
                        background: "#fdfaf5", border: "1.5px solid rgba(200,135,58,0.3)",
                        color: "#2d2d2d", fontSize: "0.85rem", outline: "none", fontFamily: "inherit" }}
                      onFocus={(e) => {
                       e.target.style.border = "1.5px solid #C8873A";
                       e.target.style.boxShadow = "0 0 0 3px rgba(200,135,58,0.1)";
                      }}
                      onBlur={(e) => {
                        e.target.style.border = "1.5px solid rgba(46,139,87,0.3)";
                        e.target.style.boxShadow = "none";
                      }} />
                    <motion.button whileHover={{ scale: 1.06 }} whileTap={{ scale: 0.94 }}
                      onClick={sendChat} disabled={!chatInput.trim() || chatLoading}
                      style={{ width: 40, height: 40, borderRadius: 10, border: "none",
                        background: chatInput.trim() ? "#C8873A" : "rgba(200,135,58,0.15)",
                        color: chatInput.trim() ? "#fff" : "#9ca3af",
                        cursor: chatInput.trim() ? "pointer" : "not-allowed",
                        display: "flex", alignItems: "center", justifyContent: "center" }}>
                      <Send size={15} />
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
