from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, override_settings
from app.stocks.services import FinnhubService, FinnhubServiceError


@override_settings(FINNHUB_API_KEY="test-key")
@patch.object(FinnhubService, "_rate_limit")
class FinnhubServiceTest(SimpleTestCase):

    @patch("app.stocks.services.finnhub.Client")
    def test_get_quote_success(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.quote.return_value = {
            "c": 150.0, "d": 2.5, "dp": 1.69,
            "h": 151.0, "l": 148.0, "o": 149.0, "pc": 147.5, "t": 1234567890,
        }
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        result = service.get_quote("AAPL")

        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["current_price"], 150.0)
        self.assertEqual(result["change"], 2.5)
        self.assertEqual(result["change_percent"], 1.69)
        mock_client.quote.assert_called_once_with("AAPL")

    @patch("app.stocks.services.finnhub.Client")
    def test_get_quote_no_data(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.quote.return_value = {"c": 0, "d": 0, "dp": 0, "h": 0, "l": 0, "o": 0, "pc": 0}
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        with self.assertRaises(FinnhubServiceError) as ctx:
            service.get_quote("INVALID")
        self.assertIn("No data found", str(ctx.exception))

    @patch("app.stocks.services.finnhub.Client")
    def test_get_quote_api_error(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.quote.side_effect = Exception("API timeout")
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        with self.assertRaises(FinnhubServiceError) as ctx:
            service.get_quote("AAPL")
        self.assertIn("Failed to fetch quote", str(ctx.exception))

    @patch("app.stocks.services.finnhub.Client")
    def test_search_symbol_success(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.symbol_lookup.return_value = {
            "count": 2,
            "result": [
                {"symbol": "AAPL", "description": "Apple Inc", "type": "Common Stock"},
                {"symbol": "AAPL.MX", "description": "Apple Inc", "type": "Common Stock"},
            ],
        }
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        results = service.search_symbol("AAPL")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["symbol"], "AAPL")
        self.assertEqual(results[0]["description"], "Apple Inc")

    @patch("app.stocks.services.finnhub.Client")
    def test_search_symbol_empty(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.symbol_lookup.return_value = {"count": 0, "result": []}
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        results = service.search_symbol("XYZNONEXISTENT")
        self.assertEqual(results, [])

    @patch("app.stocks.services.http_requests.get")
    @patch("app.stocks.services.finnhub.Client")
    def test_get_candles_success(self, mock_client_cls, mock_get, _mock_rl):
        mock_client_cls.return_value = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "Time Series (Daily)": {
                "2026-04-10": {"1. open": "100.0", "2. high": "102.0", "3. low": "99.0", "4. close": "101.0", "5. volume": "1000000"},
                "2026-04-11": {"1. open": "101.0", "2. high": "103.0", "3. low": "100.0", "4. close": "102.0", "5. volume": "1100000"},
            }
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        service = FinnhubService()
        with self.settings(ALPHA_VANTAGE_API_KEY="test-key"):
            result = service.get_candles("AAPL", "1m")

        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(len(result["candles"]), 2)
        self.assertEqual(result["candles"][0]["close"], 101.0)
        self.assertEqual(result["candles"][0]["volume"], 1000000)
        self.assertEqual(result["candles"][0]["time"], "2026-04-10")

    @patch("app.stocks.services.http_requests.get")
    @patch("app.stocks.services.finnhub.Client")
    def test_get_candles_no_data(self, mock_client_cls, mock_get, _mock_rl):
        mock_client_cls.return_value = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"Time Series (Daily)": {}}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        service = FinnhubService()
        with self.settings(ALPHA_VANTAGE_API_KEY="test-key"):
            result = service.get_candles("AAPL", "1m")
        self.assertEqual(result["candles"], [])

    @patch("app.stocks.services.finnhub.Client")
    def test_get_candles_invalid_period(self, mock_client_cls, _mock_rl):
        mock_client_cls.return_value = MagicMock()

        service = FinnhubService()
        with self.settings(ALPHA_VANTAGE_API_KEY="test-key"):
            with self.assertRaises(FinnhubServiceError) as ctx:
                service.get_candles("AAPL", "invalid")
        self.assertIn("Invalid period", str(ctx.exception))

    @patch("app.stocks.services.finnhub.Client")
    def test_get_market_indices(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.quote.return_value = {
            "c": 500.0, "d": 5.0, "dp": 1.0,
            "h": 505.0, "l": 495.0, "o": 498.0, "pc": 495.0, "t": 0,
        }
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        results = service.get_market_indices()

        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["name"], "S&P 500")
        self.assertEqual(results[3]["name"], "CAC 40")

    @patch("app.stocks.services.finnhub.Client")
    def test_get_market_indices_partial_failure(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        call_count = 0

        def side_effect(ticker):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"c": 500.0, "d": 5.0, "dp": 1.0, "h": 505.0, "l": 495.0, "o": 498.0, "pc": 495.0, "t": 0}
            raise Exception("API error")

        mock_client.quote.side_effect = side_effect
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        results = service.get_market_indices()

        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["current_price"], 500.0)
        self.assertIsNone(results[1]["current_price"])
        self.assertEqual(results[1]["error"], "Data unavailable")

    def test_missing_api_key_raises(self, _mock_rl):
        with self.settings(FINNHUB_API_KEY=""):
            with self.assertRaises(FinnhubServiceError) as ctx:
                FinnhubService()
            self.assertIn("not configured", str(ctx.exception))

    @patch("app.stocks.services.finnhub.Client")
    def test_ticker_uppercased(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.quote.return_value = {
            "c": 150.0, "d": 2.5, "dp": 1.69,
            "h": 151.0, "l": 148.0, "o": 149.0, "pc": 147.5, "t": 0,
        }
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        result = service.get_quote("aapl")

        self.assertEqual(result["symbol"], "AAPL")
        mock_client.quote.assert_called_once_with("AAPL")
