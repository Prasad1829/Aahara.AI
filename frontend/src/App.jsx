import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from "react-router-dom";
import ScrollToTop from "./components/ScrollToTop";
import PrivateLayout from "./components/PrivateLayout";
import Landing from "./pages/Landing";
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
import Wishlist from "./pages/Wishlist";

function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/auth" replace />;
}

function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const [showSplash, setShowSplash] = useState(
    () => sessionStorage.getItem("ahara_splash_seen") !== "1"
  );

  useEffect(() => {
    if (!showSplash && location.pathname === "/") {
      navigate("/landing", { replace: true });
    }
  }, [showSplash, location.pathname, navigate]);

  return (
    <>
      {showSplash && (
        <div style={{ position: "fixed", inset: 0, zIndex: 9999 }}>
          <SplashScreen
            onDone={() => {
              sessionStorage.setItem("ahara_splash_seen", "1");
              setShowSplash(false);
              if (location.pathname === "/") {
                navigate("/landing", { replace: true });
              }
            }}
          />
        </div>
      )}

      <Routes>
        <Route path="/" element={<Navigate to="/landing" replace />} />
        <Route path="/landing" element={<Landing />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route element={<PrivateRoute><PrivateLayout /></PrivateRoute>}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload-image" element={<UploadImagePage />} />
          <Route path="/select-vegetables" element={<SelectVegetablesPage />} />
          <Route path="/manual-entry" element={<ManualEntryPage />} />
          <Route path="/recipe/:recipeName" element={<RecipeDetailPage />} />
          <Route path="/wishlist" element={<Wishlist />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <AppShell />
    </BrowserRouter>
  );
}
