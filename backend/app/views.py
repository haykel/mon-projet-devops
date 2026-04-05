from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def hello(request):
    return Response({"message": "Hello World"})

@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})
