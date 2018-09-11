#!/usr/bin/env python
# -*- coding: utf-8 -*-
# auth : wangling

from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy import create_engine
from mysql.user import UserModel
from settings import MYSQL_KTV
import random
import logging
from tornado.options import options
# engine = create_engine("mysql+pymysql://mombaby:098f6bcd4621d373cade4e832627b4f6@127.0.0.1:3308/erp", max_overflow=5)

def create_session(engine):
    if not engine:
        return None
    session = scoped_session(sessionmaker(bind=engine))
    return session()

class Database(object):
    def __init__ (self):
        self.schema = 'mysql://%s:%s@%s:%d/%s?charset=utf8'
        self.session = {
            'm': {},
            's': {}
        }
        # self.kwargs = {
        #     'pool_recycle': 3600,
        #     'echo': options.debug,
        #
        #     'echo_pool': options.debug
        # }

        self.init_session ()
        self.user=UserModel(self)


    def _session(self, user, passwd, host, port, db, master=True):
        schema = self.schema % (user, passwd, host, port, db)
        # engine = create_engine(schema, **self.kwargs)
        engine = create_engine (schema)
        session = create_session(engine)
        print('%s: %s' % ('master' if master else 'slave', schema))
        return session


    def init_session (self):
        master, slaves, dbs = MYSQL_KTV ['master'], MYSQL_KTV ['slaves'], MYSQL_KTV ['dbs']
        for db in dbs:
            self.session ['s'] [db] = []

            session = self._session (master ['user'], master ['pass'], master ['host'], master ['port'], db)
            self.session ['m'] [db] = session

            for slave in slaves:
                session = self._session (slave ['user'], slave ['pass'], slave ['host'], slave ['port'], db,
                                         master=False)
                self.session ['s'] [db].append (session)

    def get_session(self, db, master=False):
        if not master:
            sessions = self.session['s'][db]
            if len(sessions) > 0:
                session = random.choice(sessions)
                return session
        session = self.session['m'][db]
        return session

    @classmethod
    def instance (cls):
        name = 'singleton'
        if not hasattr (cls, name):
            setattr (cls, name, cls ())
        return getattr (cls, name)

    def close (self):

        def shut (ins):
            try:
                ins.commit ()
            except:
                logging.error ('MySQL server has gone away. ignore.')
            finally:
                ins.close ()

        for db in MYSQL_KTV ['dbs']:
            shut (self.session ['m'] [db])
            for session in self.session ['s'] [db]:
                shut (session)

# global, called by control
pdb = Database.instance()
#
# #定义初始化数据库函数
# def init_db():
#     Base.metadata.create_all(engine)
#
# #顶固删除数据库函数
# def drop_db():
#     Base.metadata.drop_all(engine)

# drop_db()
# init_db()

# #创建mysql操作对象
# Session = sessionmaker(bind=engine)
# session = Session()
#增加
# obj = Users(name='alex',extra='sb')
# session.add(obj)
# #add_all 列表形式
# session.add_all([
#     Users(name='cc',extra='cow'),
#     Users(name='dd',extra='cowcow')
# ])
# #提交
# session.commit()

