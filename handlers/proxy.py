import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado_http_auth import DigestAuthMixin, auth_required

# In production these credentials would be coming from an external source
credentials = {'admin': 'Password1'}


class ProxyHandler(DigestAuthMixin, tornado.web.RequestHandler):
    """
    This handler prompts for and verifies authentication, then proxies the
    request to the web service running on port 8080
    """

    @auth_required(realm='TopSecret', auth_func=credentials.get)
    async def get(self):
        resp = await tornado.httpclient.AsyncHTTPClient().fetch(
            'http://web:8080/', headers=self.request.headers)
        self.set_status(resp.code)
        for k, v in resp.headers.get_all():
            self.add_header(k, v)
        self.write(resp.body)
