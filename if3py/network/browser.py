#!/usr/bin/env python

from selenium import webdriver
from if3py.utils import logger 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class Selenium:
	def __init__(self, driver_type):
		self.driver_type = driver_type
		if self.driver_type == 'firefox':
			self.self.driver = webdriver.Firefox()
		elif self.driver_type == 'phantom':
			self.driver = webdriver.PhantomJS()
		self.driver.implicitly_wait(10)
		self.driver.set_window_size(1120, 550)

	def get_page_source(self, url):
		logger.info('browser load url: {0}'.format(url))
		self.driver.wait = WebDriverWait(self.driver, 5)
		self.driver.get(url)
		html = self.driver.page_source
		#self.driver.quit()
		return html

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