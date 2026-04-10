from django.urls import path, include
from app.views import hello, health

urlpatterns = [
    path("api/hello/", hello),
    path("api/", include("app.stocks.urls")),
    path("health/", health),
]
