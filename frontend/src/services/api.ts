import axios from "axios";
import keycloak from "../keycloak";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  if (keycloak.token) {
    config.headers.Authorization = `Bearer ${keycloak.token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        await keycloak.updateToken(30);
        error.config.headers.Authorization = `Bearer ${keycloak.token}`;
        return api.request(error.config);
      } catch {
        keycloak.logout();
      }
    }
    return Promise.reject(error);
  }
);

export interface StockQuote {
  symbol: string;
  current_price: number;
  change: number | null;
  change_percent: number | null;
  high?: number;
  low?: number;
  open?: number;
  previous_close?: number;
  volume?: number;
  timestamp?: number;
}

export interface SearchResult {
  symbol: string;
  description: string;
  type: string;
}

export interface Candle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface MarketIndex {
  name: string;
  index_symbol: string;
  symbol: string;
  current_price: number | null;
  change: number | null;
  change_percent: number | null;
  error?: string;
}

export async function searchStocks(query: string): Promise<SearchResult[]> {
  const { data } = await api.get("/stocks/search/", { params: { q: query } });
  return data.results;
}

export async function getStock(ticker: string): Promise<StockQuote> {
  const { data } = await api.get(`/stocks/${ticker}/`);
  return data;
}

export async function getStockHistory(
  ticker: string,
  period: string = "1m"
): Promise<{ symbol: string; candles: Candle[] }> {
  const { data } = await api.get(`/stocks/${ticker}/history/`, {
    params: { period },
  });
  return data;
}

export async function getIndices(): Promise<MarketIndex[]> {
  const { data } = await api.get("/markets/indices/");
  return data.indices;
}

export default api;
