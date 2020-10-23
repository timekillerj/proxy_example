from tornado.testing import AsyncHTTPTestCase

import proxy


class TestHealth(AsyncHTTPTestCase):
    def get_app(self):
        return proxy.Application()

    def test_health(self):
        response = self.fetch('/health')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'OK')


class TestRedirectSSL(AsyncHTTPTestCase):
    def get_app(self):
        return proxy.RedirectSSL()

    def test_redirect_ssl(self):
        response = self.fetch('/', follow_redirects=False)
        self.assertEqual(response.code, 301)


class TestNotFound(AsyncHTTPTestCase):
    def get_app(self):
        return proxy.Application()

    def test_not_found_handler(self):
        response = self.fetch('/no_such_url')
        self.assertEqual(response.code, 404)
        self.assertEqual(response.body, b'404: Not Found')


class TestAuthPrompt(AsyncHTTPTestCase):
    def get_app(self):
        return proxy.Application()

    def test_basic_auth_prompt(self):
        response = self.fetch('/uj47G/index.htm')
        self.assertEqual(response.code, 401)
