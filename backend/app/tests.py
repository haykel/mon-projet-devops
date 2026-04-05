from django.test import SimpleTestCase, RequestFactory
from app.views import hello, health


class HelloTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_hello_returns_message(self):
        request = self.factory.get("/api/hello")
        response = hello(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "Hello World"})

    def test_health_returns_ok(self):
        request = self.factory.get("/health")
        response = health(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "ok"})
