from django.urls import path
from app.views import hello, health

urlpatterns = [
    path("api/hello/", hello),
    path("health/", health),
]
