import { useParams, useNavigate } from "react-router-dom";
import { useStockDetail } from "../hooks/useStock";
import StockCard from "../components/StockCard/StockCard";
import StockChart from "../components/Chart/StockChart";

export default function Stock() {
  const { ticker } = useParams<{ ticker: string }>();
  const navigate = useNavigate();
  const { quote, loading, error, refresh } = useStockDetail(ticker);

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "24px 16px" }}>
      {/* Back button */}
      <button
        onClick={() => navigate("/")}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          padding: "8px 16px",
          borderRadius: 6,
          border: "1px solid #e2e8f0",
          background: "#fff",
          cursor: "pointer",
          fontSize: 14,
          marginBottom: 24,
        }}
      >
        ← Retour
      </button>

      {loading && !quote && (
        <div style={{ padding: 40, textAlign: "center", color: "#94a3b8" }}>
          Chargement...
        </div>
      )}

      {error && (
        <div style={{ padding: 40, textAlign: "center", color: "#dc2626" }}>
          {error}
        </div>
      )}

      {quote && (
        <>
          <div style={{ marginBottom: 24 }}>
            <StockCard quote={quote} />
          </div>

          {/* Additional info */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
              gap: 12,
              marginBottom: 32,
            }}
          >
            {quote.volume != null && (
              <div
                style={{
                  background: "#f8fafc",
                  borderRadius: 8,
                  padding: 16,
                }}
              >
                <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 4 }}>
                  Volume
                </div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>
                  {quote.volume.toLocaleString()}
                </div>
              </div>
            )}
            {quote.high != null && (
              <div
                style={{
                  background: "#f8fafc",
                  borderRadius: 8,
                  padding: 16,
                }}
              >
                <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 4 }}>
                  Plus haut
                </div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>
                  ${quote.high.toFixed(2)}
                </div>
              </div>
            )}
            {quote.low != null && (
              <div
                style={{
                  background: "#f8fafc",
                  borderRadius: 8,
                  padding: 16,
                }}
              >
                <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 4 }}>
                  Plus bas
                </div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>
                  ${quote.low.toFixed(2)}
                </div>
              </div>
            )}
            {quote.open != null && (
              <div
                style={{
                  background: "#f8fafc",
                  borderRadius: 8,
                  padding: 16,
                }}
              >
                <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 4 }}>
                  Ouverture
                </div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>
                  ${quote.open.toFixed(2)}
                </div>
              </div>
            )}
            {quote.previous_close != null && (
              <div
                style={{
                  background: "#f8fafc",
                  borderRadius: 8,
                  padding: 16,
                }}
              >
                <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 4 }}>
                  Clôture préc.
                </div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>
                  ${quote.previous_close.toFixed(2)}
                </div>
              </div>
            )}
          </div>

          {/* Chart */}
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>
            Historique des prix
          </h2>
          <StockChart ticker={ticker!} />

          {/* Refresh */}
          <div style={{ marginTop: 24, textAlign: "center" }}>
            <button
              onClick={refresh}
              style={{
                padding: "8px 20px",
                borderRadius: 6,
                border: "1px solid #e2e8f0",
                background: "#fff",
                cursor: "pointer",
                fontSize: 14,
              }}
            >
              Actualiser
            </button>
            <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 8 }}>
              Mise à jour automatique toutes les 60s
            </div>
          </div>
        </>
      )}
    </div>
  );
}
