import Navbar from "../components/Navbar";

export default function History() {
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
          History
        </h1>
        <p style={{ color: "#9CA3AF", marginBottom: "24px" }}>
          View your past recipe generations and ingredient detections. This is a placeholder page where you can later
          connect to backend history endpoints.
        </p>

        <div
          style={{
            padding: "20px",
            borderRadius: "16px",
            background: "rgba(15,23,42,0.8)",
            border: "1px solid rgba(148,163,184,0.2)",
            textAlign: "center",
            color: "#6B7280",
          }}
        >
          No history to show yet.
        </div>
      </main>
    </div>
  );
}
