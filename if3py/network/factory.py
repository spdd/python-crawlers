#!/usr/bin/env python

from if3py.network.utils import is_checker_blocked
from if3py.network.browser import Selenium, SimpleRequests

class NetworkFactory:
	
	def __init__(self):
		self.is_checker_blocked = is_checker_blocked()

	def create_browser(self, type):
		# get actual browser depend on a site has
		# a blocking system for crawlers
		if self.is_checker_blocked:
			return Selenium()
		else:
			return SimpleRequests()