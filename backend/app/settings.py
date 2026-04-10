import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-in-prod")

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "app.urls"

DATABASES = {}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Finnhub
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")

# Keycloak
KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "http://localhost:8180")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "investissement")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "backend")

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "app.authentication.KeycloakAuthentication",
    ],
    "UNAUTHENTICATED_USER": None,
}
