import tornado.web
import os
from control import ctrl

class PoHandler(tornado.web.RequestHandler):
    def post (self):
        noun1 = self.get_argument ('noun1','wangling')
        noun2 = self.get_argument ('noun2','lisi')
        verb = self.get_argument ('verb','wangwu')
        noun3 = self.get_argument ('noun3','zhaoliu')
        self.render(os.path.join (os.path.abspath (os.path.join (os.getcwd ())), "static/poem.html"),roads=noun1, wood=noun2, made=verb,
                     difference=noun3)

class WHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(os.path.join(os.path.abspath(os.path.join(os.getcwd())),"static/index.html"))
    def post(self):

        res = ctrl.user_add.add_user()
        self.send_json ({
            'data': res
        })