#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import logging
import traceback
import datetime
import time

from decimal import Decimal
from tornado import web, gen
from control import ctrl
from settings import ERR
from lib import utils

from urllib.parse import unquote
# from settings import WX_CONF,MICRO_WEBSITE_MODULE
from tornado.httputil import url_concat
from tornado import httpclient
from tornado.ioloop import IOLoop
from tornado.options import options


_COOKIE_KEY =lambda ktv_id, appid: 'GZH_openid_3_%s_%s'%(str(ktv_id), appid)


class BaseHandler(web.RequestHandler):

    MOBILE_PATTERN = re.compile('(Mobile|iPod|iPhone|Android|Opera Mini|BlackBerry|webOS|UCWEB|Blazer|PSP)', re.I)

    def _d(self):
        user_agent = self.request.headers.get('user-agent', '').split(';')
        if 'thunder' in user_agent[-1]:
            return 'pc'
        if self.MOBILE_PATTERN.search(self.request.headers.get('user-agent', '')):
            return 'mobile'
        else:
            return 'pc'

    def initialize(self):
        ctrl.pdb.close()

    def on_finish(self):
        ctrl.pdb.close()

    def json_format(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, Decimal):
            return ('%.2f' % obj)
        if isinstance(obj, bytes):
            return obj.decode()

    def has_argument(self, name):
        return name in self.request.arguments

    def send_json(self, data={}, errcode=200, errmsg='', status_code=200):
        res = {
            'errcode': errcode,
            'errmsg': errmsg if errmsg else ERR[errcode]
        }
        res.update(data)

        if errcode > 200:
            logging.error(res)

        json_str = json.dumps(res, default=self.json_format)
        if options.debug:
            logging.info('%s, path: %s, arguments: %s, body: %s, cookies: %s, response: %s' % (self.request.method, self.request.path, self.request.arguments, self.request.body, self.request.cookies, json_str))

        jsonp = self.get_argument('jsonp', '')
        if jsonp:
            jsonp = re.sub(r'[^\w\.]', '', jsonp)
            self.set_header('Content-Type', 'text/javascript; charet=UTF-8')
            json_str = '%s(%s)' % (jsonp, json_str)
        else:
            self.set_header('Content-Type', 'application/json')

        origin = self.request.headers.get("Origin")
        origin = '*' if not origin else origin
        if self.request.path in ('/common/order', '/upyun/getfile', '/upyun/getfile/info', '/erp/ktv/commonapi', '/wx/share/config'):
            self.set_header("Access-Control-Allow-Origin", origin)
            self.set_header("Access-Control-Allow-Credentials", "true")
            self.set_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
            self.set_header('Access-Control-Allow-Methods', 'GET')

        if options.debug:
            self.set_header("Access-Control-Allow-Origin", origin)
            self.set_header("Access-Control-Allow-Credentials", "true")
            self.set_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
            self.set_header('Access-Control-Allow-Methods', '*')

        origin = self.request.headers.get("Origin")
        origin = '*' if not origin else origin
        self.set_header("Access-Control-Allow-Origin", origin)
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.set_header('Access-Control-Allow-Methods', 'OPTIONS, GET, POST, PUT, DELETE')

        if errcode != 200 and self.request.path.startswith('/by/top'):
            status_code = 500
        self.set_status(status_code)
        self.write(json_str)
        self.finish()

    def dict_args(self):
        _rq_args = self.request.arguments
        rq_args = dict([(k, _rq_args[k][0]) for k in _rq_args])
        return rq_args

    def _full_url(self):
        try:
            return self.full_url
        except:
            return self.request.full_url()

    def render2(self, *args, **kwargs):
        if self.get_argument('json', ''):
            kwargs.pop('config', '')
            self.send_json(kwargs)
            return

        self.render(*args, **kwargs)

    def render_empty(self):
        self.render('error.html', err_title='抱歉，出错了', err_info='抱歉，出错了')

    def write_error(self, status_code=200, **kwargs):
        if 'exc_info' in kwargs:
            err_object = kwargs['exc_info'][1]
            traceback.format_exception(*kwargs['exc_info'])

            if isinstance(err_object, utils.APIError):
                err_info = err_object.kwargs
                self.send_json(**err_info)
                return
        if not options.debug:
            self.render_empty()
        self.captureException(**kwargs)

    def render(self, template_name, **kwargs):
        tp = self.get_argument('tp', '')
        if tp=='out':
            kwargs.update({'show_menu': 1, 'tp': 'out'})
        else:
            kwargs.update({'show_menu': 0, 'tp': tp})

        if options.debug:
            logging.info('render args: %s' % kwargs)
        return super(BaseHandler, self).render(template_name, **kwargs)

    def is_actived_ktv(self, ktv_id):
        if ctrl.rs.sismember('ktv_custom_active_ktvs', str(ktv_id).encode()):
            expire_date = ctrl.rs.hget('ktv_custom_active_expire',ktv_id)
            if not expire_date:
                return 0
            expire_date = (datetime.datetime.strptime(expire_date.decode(), '%Y-%m-%d')+ datetime.timedelta(days=1))
            if datetime.datetime.now()>expire_date:
                return 0
            return 1

        return 0


    def is_coupon_actived_ktv(self, ktv_id):
        if options.debug:
            return True
        if ctrl.rs.sismember('ktv_custom_coupon_active_ktvs', str(ktv_id).encode()):
            return True
        return False

    def need_active(self):
        self.render('error.html', err_title='功能未激活', err_info='该功能未激活，请联系您的代理商激活')



    def log_sentry(self, data):
        self.captureMessage(data, stack=True)

    def get_gzh_user(self, openid, ktv_id):
        gzh_user = ctrl.web.get_gzh_user(openid, ktv_id)
        if not gzh_user:
            gzh_user = ctrl.web.add_gzh_user(openid=openid, ktv_id=ktv_id)
        return gzh_user

    def is_ktv_module_setted(self, ktv_id, tp='coupon'):
        if ctrl.gzh.check_ktv_set_module_ctl(ktv_id, tp):
            return 1

        return 0

    def is_ktv_setted(self, ktv_id):
        if ctrl.gzh.check_ktv_setted_ctl(ktv_id):
            return 1
        return 0

    def need_active(self):
        self.render('error.html', err_title='功能未激活', err_info='该功能未激活，请联系XXX')

    def need_setting(self):
        self.render('error.html', err_title='功能未设置', err_info='该功能设置有误，请联系XXXX')

    def render_empty(self, err_title='XXX', err_info='该活动已过期'):
        self.render('error.html', err_title=err_title, err_info=err_info)


class AsyncHttpHandler(BaseHandler):

    def write_error(self, status_code=200, **kwargs):
        if 'exc_info' in kwargs:
            err_object = kwargs['exc_info'][1]
            traceback.format_exception(*kwargs['exc_info'])

            if isinstance(err_object, utils.APIError):
                err_info = err_object.kwargs
                self.send_json(**err_info)
                return

        self.send_json(status_code=500, errcode=50001)
        self.captureException(**kwargs)

