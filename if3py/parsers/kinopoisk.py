#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
from random import shuffle
from time import sleep
from if3py.utils import logger 
from if3py.data.sqlite import SqliteManager
from if3py.network.browser import Selenium 

TOP_250 = 'https://www.kinopoisk.ru/top/'
BASE_URL = 'https://www.kinopoisk.ru'
URL_TO_FILE = {TOP_250: 'cache/top250.htm'}

class Film(object):
	def __init__(self, film_id, url, name):
		logger.warning('created film object: {0}'.format(film_id))
		self.film_id = film_id
		self.url = url
		self.name = name
		self.img_url = ''
		super(Film, self).__init__()
		

class KinopoiskParser:

	def __init__(self, from_cache):
		self.use_selenium = True
		self.from_cache = from_cache
		if not self.use_selenium:
			self.session = requests.Session() 
		else:
			# 'phantom' or 'firefox'
			self.selenium = Selenium() 

	def get_page_source(self, url, is_wall = False):
		if self.use_selenium:
			return self.selenium.get_page_source(url, is_wall)
		else:
			request = self.session.get(url)
			return request.text

	def load_film(self, film_id, add=''):
		logger.info('load film id: {0}'.format(film_id))
		url = 'https://www.kinopoisk.ru/film/%s%s' %  (film_id, add)
		return self.get_page_source(url, is_wall = True)

	def load_film_wall(self, film_id):
		return self.load_film(film_id, add='/wall/')

	def retrive_country(self, film_id):
		text = self.load_film(film_id)
		soup = BeautifulSoup(text)
		film_country = soup.find('table', {'class': 'fotos fotos2'}).text
		return film_country


	def cache_page(self, page_content, filename):
		if not self.from_cache:
			with open('cache/{0}.html'.format(filename), 'w') as fid:
				fid.write(page_content.encode('utf8'))

	def get_page_content(self, url):
		if self.from_cache:
			return self.get_cache_from_url(url)
		else:
			return self.get_page_source(url)

	def get_cache_from_url(self, url):
		import codecs
		with codecs.open(URL_TO_FILE[url],'r') as f:
			return f.read()

	def store_file_to_db(self, film):
		pass



class ParserTop250Walls(KinopoiskParser):

	def __init__(self, from_cache):
		KinopoiskParser.__init__(self, from_cache)
		self.top_250_films = []

	def getImageUrl(self, url):
		url = '%s%s' %  (BASE_URL, url)
		text = self.get_page_source(url)

		soup = BeautifulSoup(text)
		film_table = soup.find('table', {'id': 'main_table'})
		img =film_table.find_all('img')
		img_url = img[0].get('src')
		return img_url[2:].replace('//', 'http://')

	def process_img(self, text, film):
		soup = BeautifulSoup(text)
		film_list = soup.find('table', {'class': 'fotos fotos2'})
		if film_list is None: 
			film_list = soup.find('table', {'class': 'fotos fotos1'})
			if film_list is None: # page not have wallpapers	
				logger.info('film {0} not have wallpapers'.format(film.film_id))
				return
		alla = film_list.find_all('a', href=True)
		#logger.info(alla)
		for a in alla: # get only 800x600 wallpaper
			url = a.get('href')
			img_url = self.getImageUrl(url)
			img_url = '{0}{1}'.format('http://',img_url)
			film.img_url = img_url
			self.save_img(img_url, film.film_id)
			self.save_img_url(film)
			break

	def save_img_url(self, film):
		url = '{0} {1}'.format(film.film_id, film.img_url)
		logger.info('save img url: {0}'.format(url))
		with open('cache/img_urls.txt', 'a') as the_file:
			the_file.write('{0}\n'.format(url))

	def setup_top_250_films_ids(self):
		text = self.get_page_content(TOP_250)
		self.cache_page(text, 'top250')
		soup = BeautifulSoup(text)
		all_a = soup.find_all('a', {'class': 'all'})
		for a in all_a[2:250]:
			film_id = a.get('href').replace('/', ' ').split(' ')[2]
			
			film = Film(film_id, "", self.clear_film_title(a.text))
			logger.info('film_id: {0}'.format(film.film_id))
			self.top_250_films.append(film)

			logger.info(a.text)
		shuffle(self.top_250_films)
		provider = SqliteManager()
		provider.processFilms(self.top_250_films)
		#provider.close()

	def clear_film_title(self, title):
		arr = title.split()
		arr.remove(arr[len(arr) - 1])
		return ' '.join(arr)

	def save_img(self, url, film_id):	
		logger.info('save img url: {0}'.format(url))
		img_data = requests.get(url).content
		with open('cache/images/{0}_800x600.jpg'.format(film_id), 'wb') as handler:
			handler.write(img_data)

	def setup_all(self):
		is_saved = False
		logger.info('self.top_250_films len: {0}'.format(len(self.top_250_films)))
		for film in self.top_250_films:
			text = self.load_film_wall(film.film_id)
			if text == None:
				logger.info('wall page is null')
				continue
			if not is_saved:
				pass
				#self.cache_page(text, 'films/film_{0}'.format(film.film_id))
				#is_saved = True
			#logger.info(text)
			self.process_img(text, film)
			#sleep(5)
		self.selenium.close()

	def test_setup_all(self):
		for film in self.top_250_films:
			logger.info(film.film_id)



