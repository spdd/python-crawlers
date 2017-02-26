#!/usr/bin/env python

from selenium import webdriver
from if3py.utils import logger 
import subprocess

class Selenium:
	def __init__(self, driver_type='phantom'):
		self.driver_type = driver_type
		self.init_driver()

	def init_driver(self):
		if self.driver_type == 'firefox':
			self.self.driver = webdriver.Firefox()
		elif self.driver_type == 'phantom':
			self.driver = webdriver.PhantomJS()
		self.driver.set_window_size(1120, 550)

	def get_page_source(self, url, is_wall = False):
		logger.info('browser load url: {0}'.format(url))
		
		self.browser.get(url)
		return self.browser.page_source

	# suspect tor is working
	def init_with_tor(self):
		service_args = [ '--proxy=localhost:9150', '--proxy-type=socks5', ]
		self.driver = webdriver.PhantomJS( \
			executable_path = 'path to phantomJS', \
			service_args = service_args)

	def set_user_agent(self, user_agent):
		dcap = dict(DesiredCapabilities.PHANTOMJS)
		dcap["phantomjs.page.settings.userAgent"] = ( user_agent )
		self.driver = webdriver.PhantomJS(desired_capabilities=dcap)

	def close(self):
		self.driver.close()
		self.driver.quit()
		subprocess.call(["pgrep", "phantomjs | xargs kill"])