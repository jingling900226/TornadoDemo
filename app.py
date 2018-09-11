from tornado import web

import uuid
import base64
import os
import sys
from tornado.httpserver import HTTPServer

STATIC_PATH = os.path.join(sys.path[0], 'static')
URLS=[(
    # r'192\.168\.9\.5:8888',
    r'1\.119\.144\.204:9222',
        (r'/(.*\.txt)', web.StaticFileHandler, {'path': STATIC_PATH}),
        (r'/','handler.test.WHandler'),
        # (r'/','handler.test.MainHandler'),
        # (r'/p','handler.test.PoHandler')
        (r'/card', 'handler.test.PoHandler')

)]
TPL_PATH = os.path.join(sys.path[0], 'static')
class Application(web.Application):
    def __init__(self):
        settings = {
            'xsrf_cookies': False,
            'compress_response': True,
            # 'ui_modules': uimodules,
            # 'ui_methods': uimethods,
            'static_path': STATIC_PATH,
            'cookie_secret': base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        }
        web.Application.__init__(self, **settings)
        for i in URLS:
            host = '.*$'
            handlers=i[1:]
            self.add_handlers (host,handlers)


def run():
    application = Application ()
    http_server = HTTPServer(application,xheaders=True)
    http_server.listen(9100)
    print('running on port 9100')



