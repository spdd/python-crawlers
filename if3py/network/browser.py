#!/usr/bin/env python

from selenium import webdriver
import requests

from if3py.utils import logger 

import subprocess

TAG = 'BROWSER'

class BaseBrowser:
	def __init__(self):
		self.PRESIX = 'BASE'

	def init_session(self):
		raise NotImplementedError

	def get_page_source(self, url):
		logger.info(TAG, '{0} load url: {1}'.format(self.PRESIX, url))

	def close(self):
		pass

class Selenium(BaseBrowser):
	def __init__(self, driver_type='phantom'):
		self.PRESIX = 'SELENIUM'
		self.driver_type = driver_type
		#self.init_session()

	def init_session(self):
		if self.driver_type == 'firefox':
			self.self.driver = webdriver.Firefox()
		elif self.driver_type == 'phantom':
			self.driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
		self.driver.set_window_size(1120, 550)

	def get_page_source(self, url):
		logger.info(TAG, 'browser load url: {0}'.format(url))
		self.init_session()
		self.driver.get(url)
		html = self.driver.page_source
		self.close()
		return html

	# suspect tor is working
	def init_with_tor(self):
		service_args = [ '--proxy=localhost:9150', '--proxy-type=socks5', ]
		self.driver = webdriver.PhantomJS( \
			executable_path = '/usr/local/bin/phantomjs', \
			service_args = service_args)

	def set_user_agent(self, user_agent):
		dcap = dict(DesiredCapabilities.PHANTOMJS)
		dcap["phantomjs.page.settings.userAgent"] = ( user_agent )
		self.driver = webdriver.PhantomJS(desired_capabilities=dcap)

	def close(self):
		self.driver.close()
		self.driver.quit()
		subprocess.call(["pgrep", "phantomjs | xargs kill"])


class SimpleRequests(BaseBrowser):
	def __init__(self):
		self.PRESIX = 'REQUESTS'
		self.init_session()

	def init_session(self):
		self.session = requests.Session() 

	def get_page_source(self, url):
		super.get_page_source(url)
		request = self.session.get(url)
		return request.text

	def close(self):
		pass
