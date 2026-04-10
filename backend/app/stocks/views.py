from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from app.authentication import KeycloakAuthentication, require_role
from app.stocks.services import FinnhubService, FinnhubServiceError


@api_view(["GET"])
@authentication_classes([KeycloakAuthentication])
@require_role("user")
def search_stocks(request):
    """GET /api/stocks/search/?q=AAPL"""
    query = request.query_params.get("q", "").strip()
    if not query:
        return Response(
            {"error": "Query parameter 'q' is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        service = FinnhubService()
        results = service.search_symbol(query)
        return Response({"results": results})
    except FinnhubServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["GET"])
@authentication_classes([KeycloakAuthentication])
@require_role("user")
def stock_detail(request, ticker):
    """GET /api/stocks/{ticker}/"""
    try:
        service = FinnhubService()
        quote = service.get_quote(ticker)
        return Response(quote)
    except FinnhubServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["GET"])
@authentication_classes([KeycloakAuthentication])
@require_role("user")
def stock_history(request, ticker):
    """GET /api/stocks/{ticker}/history/?period=1m"""
    period = request.query_params.get("period", "1m")

    try:
        service = FinnhubService()
        candles = service.get_candles(ticker, period)
        return Response(candles)
    except FinnhubServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["GET"])
@authentication_classes([KeycloakAuthentication])
@require_role("user")
def market_indices(request):
    """GET /api/stocks/markets/indices/"""
    try:
        service = FinnhubService()
        indices = service.get_market_indices()
        return Response({"indices": indices})
    except FinnhubServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
