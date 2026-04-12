import time

import finnhub
import requests as http_requests
from django.conf import settings


class FinnhubServiceError(Exception):
    pass


class FinnhubService:
    """Client wrapper around the Finnhub API with rate-limit handling."""

    # Finnhub free tier: 60 calls/minute
    _last_call_time = 0.0
    _min_interval = 1.0  # seconds between calls

    def __init__(self):
        api_key = settings.FINNHUB_API_KEY
        if not api_key:
            raise FinnhubServiceError("FINNHUB_API_KEY is not configured")
        self.client = finnhub.Client(api_key=api_key)

    def _rate_limit(self):
        """Enforce minimum interval between API calls."""
        now = time.time()
        elapsed = now - FinnhubService._last_call_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        FinnhubService._last_call_time = time.time()

    def get_quote(self, ticker: str) -> dict:
        """Get current price quote for a ticker symbol.

        Returns:
            {
                "symbol": "AAPL",
                "current_price": 150.0,
                "change": 2.5,
                "change_percent": 1.69,
                "high": 151.0,
                "low": 148.0,
                "open": 149.0,
                "previous_close": 147.5,
                "timestamp": 1234567890
            }
        """
        self._rate_limit()
        try:
            data = self.client.quote(ticker.upper())
        except Exception as e:
            raise FinnhubServiceError(f"Failed to fetch quote for {ticker}: {e}")

        if not data or data.get("c", 0) == 0:
            raise FinnhubServiceError(f"No data found for ticker: {ticker}")

        return {
            "symbol": ticker.upper(),
            "current_price": data["c"],
            "change": data["d"],
            "change_percent": data["dp"],
            "high": data["h"],
            "low": data["l"],
            "open": data["o"],
            "previous_close": data["pc"],
            "timestamp": data.get("t", 0),
        }

    def search_symbol(self, query: str) -> list:
        """Search for stock symbols matching a query.

        Returns:
            [
                {
                    "symbol": "AAPL",
                    "description": "Apple Inc",
                    "type": "Common Stock"
                },
                ...
            ]
        """
        self._rate_limit()
        try:
            data = self.client.symbol_lookup(query)
        except Exception as e:
            raise FinnhubServiceError(f"Search failed for '{query}': {e}")

        results = data.get("result", [])
        return [
            {
                "symbol": item.get("symbol", ""),
                "description": item.get("description", ""),
                "type": item.get("type", ""),
            }
            for item in results[:20]
        ]

    def get_candles(self, ticker: str, period: str = "1m") -> dict:
        """Get historical candlestick data via Alpha Vantage TIME_SERIES_DAILY.

        Finnhub returns 403 on candles with the free plan, so we use
        Alpha Vantage as the data source for historical OHLCV.

        Args:
            ticker: Stock symbol
            period: Time period - 1d, 1w, 1m, 3m, 1y

        Returns:
            {
                "symbol": "AAPL",
                "candles": [
                    {"time": "2026-01-15", "open": ..., "high": ..., "low": ..., "close": ..., "volume": ...},
                    ...
                ]
            }
        """
        period_days = {
            "1d": 1,
            "1w": 7,
            "1m": 30,
            "3m": 90,
            "1y": 365,
        }

        if period not in period_days:
            raise FinnhubServiceError(
                f"Invalid period: {period}. Use: {', '.join(period_days.keys())}"
            )

        api_key = settings.ALPHA_VANTAGE_API_KEY
        if not api_key:
            raise FinnhubServiceError("ALPHA_VANTAGE_API_KEY is not configured")

        self._rate_limit()
        try:
            resp = http_requests.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "TIME_SERIES_DAILY",
                    "symbol": ticker.upper(),
                    "outputsize": "compact",
                    "apikey": api_key,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise FinnhubServiceError(f"Failed to fetch candles for {ticker}: {e}")

        if "Error Message" in data:
            raise FinnhubServiceError(f"No data found for ticker: {ticker}")

        if "Note" in data:
            raise FinnhubServiceError("Alpha Vantage API rate limit reached")

        ts = data.get("Time Series (Daily)", {})
        if not ts:
            return {"symbol": ticker.upper(), "candles": []}

        days = period_days[period]
        sorted_dates = sorted(ts.keys(), reverse=True)[:days]

        candles = []
        for date_str in reversed(sorted_dates):
            entry = ts[date_str]
            candles.append({
                "time": date_str,
                "open": float(entry["1. open"]),
                "high": float(entry["2. high"]),
                "low": float(entry["3. low"]),
                "close": float(entry["4. close"]),
                "volume": int(entry["5. volume"]),
            })

        return {"symbol": ticker.upper(), "candles": candles}

    def get_market_indices(self) -> list:
        """Get quotes for major market indices.

        Returns quotes for CAC40, S&P500, NASDAQ, DOW JONES.
        Uses ETFs as proxies since Finnhub free tier doesn't support indices directly.
        """
        indices = [
            {"symbol": "^GSPC", "etf": "SPY", "name": "S&P 500"},
            {"symbol": "^IXIC", "etf": "QQQ", "name": "NASDAQ"},
            {"symbol": "^DJI", "etf": "DIA", "name": "Dow Jones"},
            {"symbol": "^FCHI", "etf": "EWQ", "name": "CAC 40"},
        ]

        results = []
        for index in indices:
            try:
                quote = self.get_quote(index["etf"])
                quote["name"] = index["name"]
                quote["index_symbol"] = index["symbol"]
                quote["symbol"] = index["etf"]
                results.append(quote)
            except FinnhubServiceError:
                results.append(
                    {
                        "name": index["name"],
                        "index_symbol": index["symbol"],
                        "symbol": index["etf"],
                        "current_price": None,
                        "change": None,
                        "change_percent": None,
                        "error": "Data unavailable",
                    }
                )

        return results
