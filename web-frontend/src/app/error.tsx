"use client";

import { RefreshCcw, TriangleAlert } from "lucide-react";
import { useEffect } from "react";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 24 }}>
      <section style={{ maxWidth: 460, textAlign: "center" }}>
        <TriangleAlert size={34} color="#ff6b5f" />
        <h1 style={{ fontFamily: "var(--font-display)", fontSize: 40, textTransform: "uppercase", marginBottom: 8 }}>
          Dashboard interrupted
        </h1>
        <p style={{ color: "var(--muted)", lineHeight: 1.6 }}>
          The live dashboard encountered an unexpected rendering error. The backend session remains unchanged.
        </p>
        <button
          type="button"
          onClick={reset}
          style={{ marginTop: 18, border: 0, borderRadius: 12, padding: "11px 15px", color: "white", background: "var(--indigo)", fontWeight: 700, cursor: "pointer" }}
        >
          <RefreshCcw size={15} style={{ marginRight: 8, verticalAlign: -2 }} /> Retry dashboard
        </button>
      </section>
    </main>
  );
}

