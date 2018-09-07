import tornado.ioloop
import app


if __name__ == "__main__":
    app.run()
    loop = tornado.ioloop.IOLoop.instance ()
    loop.start ()
