import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from "react-router-dom";
import Landing from "./pages/Landing";        // ← was LandingPage
import SplashScreen from "./pages/SplashScreen";
import AuthPage from "./pages/AuthPage";
import Dashboard from "./pages/Dashboard";
import UploadImagePage from "./pages/UploadImagePage";
import SelectVegetablesPage from "./pages/SelectVegetablesPage";
import ManualEntryPage from "./pages/ManualEntryPage";
import RecipeDetailPage from "./pages/RecipeDetailPage";
import Profile from "./pages/Profile";
import HistoryPage from "./pages/History";
import SettingsPage from "./pages/Settings";

function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/auth" replace />;
}

function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();

  // Show splash on every full page load/refresh.
  const [showSplash, setShowSplash] = useState(true);

  const handleSplashDone = () => {
    setShowSplash(false);
    if (location.pathname === "/") {
      navigate("/landing", { replace: true });
    }
  };

  return (
    <>
      {showSplash && (
        <div style={{ position: "fixed", inset: 0, zIndex: 9999 }}>
          <SplashScreen onDone={handleSplashDone} />
        </div>
      )}

      <Routes>
        <Route path="/" element={<div />} />
        <Route path="/landing" element={<Landing />} />           {/* ← was LandingPage */}
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/upload-image" element={<PrivateRoute><UploadImagePage /></PrivateRoute>} />
        <Route path="/select-vegetables" element={<PrivateRoute><SelectVegetablesPage /></PrivateRoute>} />
        <Route path="/manual-entry" element={<PrivateRoute><ManualEntryPage /></PrivateRoute>} />
        <Route path="/recipe/:recipeName" element={<PrivateRoute><RecipeDetailPage /></PrivateRoute>} />
        <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
        <Route path="/history" element={<PrivateRoute><HistoryPage /></PrivateRoute>} />
        <Route path="/settings" element={<PrivateRoute><SettingsPage /></PrivateRoute>} />
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}