#!/usr/bin/env python
# -*- coding: utf-8 -*-
# auth : wangling
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import sessionmaker, relationship

from sqlalchemy import Column, text, or_, and_
from sqlalchemy.sql.expression import func, desc
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, ENUM, TINYINT, DATETIME, TIMESTAMP, DECIMAL, TEXT
import logging
import datetime
import control
from sqlalchemy import Column, text, or_, and_
from sqlalchemy.sql.expression import func, desc
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, ENUM, TINYINT, DATETIME, TIMESTAMP, DECIMAL, TEXT

from lib import utils
from settings import DB_KTV
from mysql.base import NotNullColumn, Base
from lib.decorator import model_to_dict, models_to_list, filter_update_data, tuple_to_dict


from mysql import base as Base
from settings import DB_KTV
# 创建单表
class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    extra = Column(String(16))

    __table_args__ = (
    UniqueConstraint('id', 'name', name='uix_id_name'),
        Index('ix_id_name', 'name', 'extra'),
    )

# 一对多
class Favor(Base):
    __tablename__ = 'favor'
    nid = Column(Integer, primary_key=True)
    caption = Column(String(50), default='red', unique=True)


class Person(Base):
    __tablename__ = 'person'
    nid = Column(Integer, primary_key=True)
    name = Column(String(32), index=True, nullable=True)
    favor_id = Column(Integer, ForeignKey("favor.nid"))

# 多对多
class ServerToGroup(Base):
    __tablename__ = 'servertogroup'
    nid = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey('server.id'))
    group_id = Column(Integer, ForeignKey('group.id'))

class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)


class Server(Base):
    __tablename__ = 'server'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String(64), unique=True, nullable=False)
    port = Column(Integer, default=22)


class UserModel(object):
    def __init__(self, pdb):
        self.pdb = pdb
        self.master=pdb.get_session(DB_KTV,master=True)
        self.slave=pdb.get_session(DB_KTV)


    def addUser(self):
        obj=Users(name='wangyi',extra='wangyi111')
        self.master.add(obj)
        self.master.commit()



