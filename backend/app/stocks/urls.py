from django.urls import path
from app.stocks import views

urlpatterns = [
    path("stocks/search/", views.search_stocks),
    path("stocks/<str:ticker>/", views.stock_detail),
    path("stocks/<str:ticker>/history/", views.stock_history),
    path("markets/indices/", views.market_indices),
]
