#!/usr/bin/env python
# -*- coding: utf-8 -*-
class UserCtrl(object):

	def __init__ (self, ctrl):
		self.ctrl = ctrl
		self.user = ctrl.pdb.user

	def __getattr__ (self, name):
		return getattr (self.user, name)

	def add_user(self):
		self.user.addUser()