import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

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

  const handleLogin = async () => {
    try {
      setErrorMessage("");
      const response = await axios.post(
        `${API_BASE}/auth/login`,
        new URLSearchParams({
          username: email,
          password,
        }),
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        }
      );

      localStorage.setItem("token", response.data.access_token);
      navigate("/dashboard");
    } catch (error) {
      setErrorMessage(parseErrorMessage(error?.response?.data, "Invalid email or password"));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-slate-50 to-cyan-50 flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="w-full max-w-md rounded-2xl border border-white/70 bg-white/80 backdrop-blur-md shadow-xl p-7"
      >
        <h2 className="text-3xl font-black text-stone-900 text-center">Welcome Back</h2>
        <p className="text-center text-stone-600 mt-2">Login to continue your recipe discovery.</p>

        <div className="mt-6 space-y-4">
          <input
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-xl border border-stone-300 px-4 py-3 outline-none focus:ring-2 focus:ring-blue-400"
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-xl border border-stone-300 px-4 py-3 outline-none focus:ring-2 focus:ring-blue-400"
          />

          <button
            onClick={handleLogin}
            className="motion-btn w-full bg-blue-600 text-white font-semibold py-3 rounded-xl hover:bg-blue-700 transition"
          >
            Login
          </button>
        </div>

        {errorMessage && (
          <div className="mt-4 rounded-lg border border-rose-300 bg-rose-50 text-rose-700 px-3 py-2 text-sm">
            {errorMessage}
          </div>
        )}

        <p className="mt-5 text-center text-stone-700">
          Don't have an account?{" "}
          <Link to="/signup" className="text-blue-700 font-semibold hover:underline">
            Signup
          </Link>
        </p>
      </motion.div>
    </div>
  );
}

export default Login;
