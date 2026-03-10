import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import downVeg from "../assets/down_veg.png";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function AuthPage() {
  const [tab, setTab] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    setEmail("");
    setPassword("");
  }, []);

  const handle = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (tab === "login") {
        // LOGIN (FastAPI OAuth2PasswordRequestForm expects form-data)
        const res = await fetch(`${API}/auth/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
            username: email,
            password: password,
          }),
        });

        const data = await res.json();

        if (!res.ok) {
          alert(data.detail || "Invalid email or password");
          return;
        }

        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify({ email }));
        navigate("/dashboard");

      } else {
        // REGISTER (JSON body)
        const res = await fetch(`${API}/auth/signup`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            password,
          }),
        });

        const data = await res.json();

        if (!res.ok) {
          alert(data.detail || "Registration failed");
          return;
        }

        alert("Registration successful. Please login.");
        setEmail("");
        setPassword("");
        setTab("login");
      }

    } catch (err) {
      alert("Server error. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container" style={{ background: "#2E8B57" }}>
      <div
        className="page-content auth-container"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "'DM Sans', sans-serif",
        }}
      >
        <div className="auth-content">
        <img
          src={downVeg}
          alt="Vegetable garnish"
          className="bottom-decor-img"
          loading="lazy"
        />

        <div
          className="auth-card"
          style={{
            background: "rgba(250,246,237,0.98)",
            boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
            position: "relative",
            zIndex: 2,
          }}
        >
        <div
          className="auth-title"
          style={{
            fontFamily: "'Playfair Display', serif",
            fontWeight: 900,
            fontSize: "2.6rem",
            textAlign: "center",
            marginBottom: 4,
          }}
        >
          Aahara.AI
        </div>

        <p
          style={{
            textAlign: "center",
            color: "#6b7280",
            fontSize: "0.85rem",
            marginBottom: 24,
          }}
        >
          Access your recipe assistant
        </p>

        {/* Tab Switch */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            background: "#ede9df",
            borderRadius: 12,
            padding: 4,
            marginBottom: 24,
          }}
        >
          {["login", "register"].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              style={{
                padding: "10px",
                borderRadius: 9,
                border: "none",
                background: tab === t ? "#4a9e6b" : "transparent",
                color: tab === t ? "#fff" : "#9ca3af",
                fontWeight: 700,
                fontSize: "0.88rem",
                cursor: "pointer",
                textTransform: "capitalize",
              }}
            >
              {t}
            </button>
          ))}
        </div>

        <form onSubmit={handle}>

          <input
            type="email"
            required
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={inputStyle}
          />

          <input
            type="password"
            required
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ ...inputStyle, marginBottom: 12 }}
          />

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "10px 14px",
              borderRadius: 10,
              border: "none",
              background: "#2d2d2d",
              color: "#fff",
              fontSize: "0.95rem",
              fontWeight: 700,
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading
              ? "Please wait..."
              : tab === "login"
              ? "Login"
              : "Register"}
          </button>
        </form>
        </div>
        </div>
      </div>

      <footer className="footer">
        © {new Date().getFullYear()} Aahara.AI · Developed by Vara Prasad · Email:
        <a href="mailto:varaprasad42c4@gmail.com" style={{ marginLeft: 4 }}>
          varaprasad42c4@gmail.com
        </a>{" "}
        · Visakhapatnam
      </footer>
    </div>
  );
}

const inputStyle = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: 10,
  border: "1.5px solid rgba(200,135,58,0.2)",
  background: "#fff",
  fontSize: "0.88rem",
  color: "#2d2d2d",
  outline: "none",
  marginBottom: 12,
  boxSizing: "border-box",
};

