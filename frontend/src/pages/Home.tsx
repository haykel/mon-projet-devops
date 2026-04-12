import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import SearchBar from "../components/SearchBar/SearchBar";
import StockCard from "../components/StockCard/StockCard";
import { useKeycloak } from "../components/KeycloakProvider";
import { getIndices, getStock, MarketIndex, StockQuote } from "../services/api";

const POPULAR_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"];

export default function Home() {
  const { username, logout } = useKeycloak();
  const navigate = useNavigate();
  const [indices, setIndices] = useState<MarketIndex[]>([]);
  const [popular, setPopular] = useState<StockQuote[]>([]);
  const [loadingIndices, setLoadingIndices] = useState(true);
  const [loadingPopular, setLoadingPopular] = useState(true);

  useEffect(() => {
    getIndices()
      .then(setIndices)
      .catch(() => {})
      .finally(() => setLoadingIndices(false));

    Promise.all(POPULAR_TICKERS.map((t) => getStock(t).catch(() => null)))
      .then((results) => setPopular(results.filter(Boolean) as StockQuote[]))
      .finally(() => setLoadingPopular(false));
  }, []);

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "24px 16px" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 32,
        }}
      >
        <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0 }}>
          Investissement
        </h1>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ color: "#64748b", fontSize: 14 }}>{username}</span>
          <button
            onClick={logout}
            style={{
              padding: "6px 14px",
              borderRadius: 6,
              border: "1px solid #e2e8f0",
              background: "#fff",
              cursor: "pointer",
              fontSize: 13,
            }}
          >
            Déconnexion
          </button>
        </div>
      </div>

      {/* Search */}
      <div style={{ display: "flex", justifyContent: "center", marginBottom: 40 }}>
        <SearchBar />
      </div>

      {/* Indices */}
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>
        Indices boursiers
      </h2>
      {loadingIndices ? (
        <div style={{ color: "#94a3b8", marginBottom: 32 }}>Chargement...</div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
            gap: 16,
            marginBottom: 40,
          }}
        >
          {indices.map((idx) => (
            <div
              key={idx.symbol}
              style={{
                background: "#fff",
                border: "1px solid #e2e8f0",
                borderRadius: 12,
                padding: 16,
              }}
            >
              <div style={{ fontSize: 14, color: "#64748b", marginBottom: 4 }}>
                {idx.name}
              </div>
              {idx.current_price != null ? (
                <>
                  <div style={{ fontSize: 22, fontWeight: 700 }}>
                    ${idx.current_price.toFixed(2)}
                  </div>
                  <div
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color:
                        (idx.change_percent ?? 0) >= 0 ? "#16a34a" : "#dc2626",
                    }}
                  >
                    {(idx.change_percent ?? 0) >= 0 ? "+" : ""}
                    {idx.change_percent?.toFixed(2)}%
                  </div>
                </>
              ) : (
                <div style={{ color: "#94a3b8", fontSize: 14 }}>
                  Indisponible
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Popular stocks */}
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>
        Actions populaires
      </h2>
      {loadingPopular ? (
        <div style={{ color: "#94a3b8" }}>Chargement...</div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
            gap: 16,
          }}
        >
          {popular.map((stock) => (
            <StockCard
              key={stock.symbol}
              quote={stock}
              onClick={() => navigate(`/stock/${stock.symbol}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
