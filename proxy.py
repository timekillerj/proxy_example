#!/user/bin/env python
import logging

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


from handlers import proxy


class HealthHandler(tornado.web.RequestHandler):
    """
    This handler is meant to be used by monitoring services to verify health
    """

    async def get(self):
        self.finish('OK')


class NotFoundHandler(tornado.web.RequestHandler):
    """
    This handler returns a 404 error code for any urls we aren't expecting
    """

    def prepare(self):
        self.set_status(404)
        self.finish('404: Not Found')


class RedirectHandler(tornado.web.RequestHandler):
    """
    This handler is how we redirect http to https. It is the only handler
    used by the RedirectSSL web application.
    """

    def prepare(self):
        if self.request.protocol == "http":
            self.redirect(
                f'https://{self.request.full_url()[len("http://"):]}',
                permanent=True)


class RedirectSSL(tornado.web.Application):
    """
    This application runs on port 80 and uses the RedirectHandler to redirect
    traffic to the ssl encrypted server
    """

    def __init__(self):
        app_settings = {
            'debug': True,
            'default_handler_class': RedirectHandler,
        }

        app_handlers = []
        super(RedirectSSL, self).__init__(app_handlers, **app_settings)


class Application(tornado.web.Application):
    """
    Main application. This will run on port 443 to handle requests
    A health handler is included for monitoring.
    """

    def __init__(self):
        app_settings = {
            'debug': True,
            'default_handler_class': NotFoundHandler,
        }

        app_handlers = [
            (r'^/health/?$', HealthHandler),
            (r'^/uj47G/index.htm', proxy.ProxyHandler),
        ]
        super(Application, self).__init__(app_handlers, **app_settings)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    https_port = 443
    http_port = 80
    address = '0.0.0.0'
    logging.getLogger().setLevel(logging.INFO)

    logging.info(f'starting web on {address}:{https_port}')
    https_server = tornado.httpserver.HTTPServer(
        request_callback=Application(),
        ssl_options={
            "certfile": "/app/certs/proxy.crt",
            "keyfile": "/app/certs/proxy.key",
        })
    https_server.listen(https_port, address=address)

    logging.info(f'starting web on {address}:{http_port}')
    http_server = tornado.httpserver.HTTPServer(request_callback=RedirectSSL())
    http_server.listen(http_port, address=address)

    io_loop = tornado.ioloop.IOLoop.current()

    io_loop.start()
