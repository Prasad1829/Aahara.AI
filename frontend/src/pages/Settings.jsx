import Navbar from "../components/Navbar";

export default function Settings() {
  const user = JSON.parse(localStorage.getItem("user"));

  return (
    <div style={{ minHeight: "100vh", background: "#0B1727" }}>
      <Navbar user={user} />
      <main
        style={{
          maxWidth: "960px",
          margin: "40px auto",
          padding: "32px",
          borderRadius: "24px",
          background: "#0f172a",
          border: "1px solid rgba(148,163,184,0.3)",
          color: "#E5E7EB",
        }}
      >
        <h1
          style={{
            fontFamily: '"Playfair Display", Georgia, serif',
            fontSize: "2rem",
            marginBottom: "12px",
          }}
        >
          Settings
        </h1>
        <p style={{ color: "#9CA3AF", marginBottom: "24px" }}>
          Configure your Aahara.AI experience. This is a placeholder page where you can later add notification,
          dietary preference, and theme settings.
        </p>

        <div
          style={{
            padding: "20px",
            borderRadius: "16px",
            background: "rgba(15,23,42,0.8)",
            border: "1px solid rgba(148,163,184,0.2)",
            color: "#6B7280",
          }}
        >
          Settings controls coming soon.
        </div>
      </main>
    </div>
  );
}
