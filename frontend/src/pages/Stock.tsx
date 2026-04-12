import { useCallback, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useStockDetail, useScore, useIndicators } from "../hooks/useStock";
import StockCard from "../components/StockCard/StockCard";
import CandlestickChart from "../components/Chart/CandlestickChart";
import IndicatorPanel from "../components/Chart/IndicatorPanel";
import StockScore from "../components/StockScore/StockScore";
import ModeToggle from "../components/Chart/ModeToggle";

export default function Stock() {
  const { ticker } = useParams<{ ticker: string }>();
  const navigate = useNavigate();
  const { quote, loading, error, refresh } = useStockDetail(ticker);
  const { score } = useScore(ticker);
  const [advanced, setAdvanced] = useState(
    () => localStorage.getItem("chart-mode-advanced") === "true"
  );
  const { data: indicators } = useIndicators(
    advanced ? ticker : undefined,
    "rsi,macd,ma20,ma50,bb",
    "3m"
  );

  const handleModeChange = useCallback((adv: boolean) => {
    setAdvanced(adv);
  }, []);

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "24px 16px" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 24,
        }}
      >
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
          }}
        >
          ← Retour
        </button>
        <ModeToggle onChange={handleModeChange} />
      </div>

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
          {/* Score */}
          {score && (
            <div style={{ marginBottom: 24 }}>
              <StockScore score={score} />
            </div>
          )}

          {/* Stock card */}
          <div style={{ marginBottom: 24 }}>
            <StockCard quote={quote} />
          </div>

          {/* Info grid */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
              gap: 12,
              marginBottom: 32,
            }}
          >
            {[
              { label: "Volume", value: quote.volume?.toLocaleString() },
              { label: "Plus haut", value: quote.high != null ? `$${quote.high.toFixed(2)}` : null },
              { label: "Plus bas", value: quote.low != null ? `$${quote.low.toFixed(2)}` : null },
              { label: "Ouverture", value: quote.open != null ? `$${quote.open.toFixed(2)}` : null },
              {
                label: "Cloture prec.",
                value: quote.previous_close != null ? `$${quote.previous_close.toFixed(2)}` : null,
              },
            ]
              .filter((item) => item.value != null)
              .map((item) => (
                <div
                  key={item.label}
                  style={{ background: "#f8fafc", borderRadius: 8, padding: 16 }}
                >
                  <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 4 }}>
                    {item.label}
                  </div>
                  <div style={{ fontSize: 18, fontWeight: 700 }}>{item.value}</div>
                </div>
              ))}
          </div>

          {/* Chart */}
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>
            {advanced ? "Graphique en chandeliers" : "Historique des prix"}
          </h2>
          <CandlestickChart ticker={ticker!} advanced={advanced} />

          {/* Indicator panels (advanced mode only) */}
          {advanced && indicators && (
            <div style={{ marginTop: 24 }}>
              <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>
                Indicateurs techniques
              </h2>
              <IndicatorPanel
                indicators={indicators}
                timestamps={indicators.timestamps}
              />
            </div>
          )}

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
              Mise a jour automatique toutes les 60s
            </div>
          </div>
        </>
      )}
    </div>
  );
}
