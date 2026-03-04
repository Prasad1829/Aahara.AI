import { Link } from "react-router-dom";
import { motion } from "framer-motion";

export default function AuthChoice() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-slate-50 to-cyan-50 flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-xl rounded-3xl border border-slate-200 bg-white/90 shadow-2xl p-8 text-center"
      >
        <p className="text-xs uppercase tracking-[0.14em] font-semibold text-blue-700">Continue</p>
        <h1 className="mt-2 text-4xl font-black text-slate-900">AHARA AI</h1>
        <p className="mt-3 text-slate-600">
          Choose how you want to continue.
        </p>

        <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Link
            to="/login"
            className="motion-btn bg-blue-600 text-white font-semibold py-4 rounded-2xl hover:bg-blue-700 transition"
          >
            Login
          </Link>
          <Link
            to="/signup"
            className="motion-btn bg-white text-slate-900 font-semibold py-4 rounded-2xl border border-slate-300 hover:bg-slate-50 transition"
          >
            Register
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
