#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from random import shuffle
from if3py.utils import logger 
from if3py.parsers.kinopoisk.sqlite import arrange_films_to_db
from if3py.network.factory import NetworkFactory

import json
import re

TAG = 'KINOPOISK_PARSER'

IMG_FILE_FORMAT = 'jpg'

TOP_250 = 'https://www.kinopoisk.ru/top/'
BASE_URL = 'https://www.kinopoisk.ru'
URL_TO_FILE = {TOP_250: 'cache/top250.htm'}

class Film(object):
	def __init__(self, film_id, url, title, country):
		self.film_id = film_id
		self.url = url
		self.title = title
		self.foreign_title = ''
		self.img_url = ''
		self.country = country
		self.is_eng = False
		super(Film, self).__init__()
		

class KinopoiskParser:

	def __init__(self, from_cache = False, test_mode = False):
		self.test_mode = test_mode
		self.from_cache = from_cache

		factory = NetworkFactory()
		self.browser = factory.create_browser()

	def get_page_source(self, url, is_wall = False, film_id = None):
		if film_id is not None and self.check_cached_film(film_id):
			return self.get_cached_film(film_id)
		html = self.browser.get_page_source(url)

		if film_id is not None:
			logger.info(TAG, 'caching page: {0}'.format(film_id))
			self.cache_page(html, film_id)
		return html

	def load_film(self, film_id, add=''):
		logger.info(TAG, 'load film id: {0}'.format(film_id))
		url = '%s/film/%s%s' %  (BASE_URL, film_id, add)
		return self.get_page_source(url, is_wall = True, film_id = film_id)

	def load_film_wall(self, film_id):
		return self.load_film(film_id, add='/wall/')

	def get_json_film_info_with_id(self, film_id):
		html = self.load_film(film_id)
		soup = BeautifulSoup(html)

		if html is None:
			logger.info(TAG, 'film with id {0} not found'.format(film_id))
			return None

		film_hearder = soup.find('div', {'class', 'feature_film_background country_num1'})
		title_h1 = film_hearder.find('h1', {'class', 'moviename-big'})
		foreign_title_h1 = film_hearder.find('span')

		title = title_h1.get_text()
		foreign_title = foreign_title_h1.get_text()

		film_table = soup.find('table', {'class': 'info'})
		all_tr = film_table.find_all('tr')

		keys = ['year', 'country', 'tagline_ru', 'director',
				 'genre', 'dollar', 'time']
		indxs = [{'num':0, 'is_a':True},
				{'num':1, 'is_a':True},
				{'num':2, 'is_a':False},
				{'num':3, 'is_a':True},
				{'num':10, 'is_a':True},
				{'num':11, 'is_a':True},
				{'num':19, 'is_a':False}]

		film_json = {}
		for i, tr in enumerate(all_tr):
			if  indxs[0]['num'] == i:
				td = tr.find_all('td')[1]
				text = td.find_all('a')[0].get_text() if indxs[0]['is_a'] else td.get_text()
				film_json[keys[0]] = text
				indxs.pop(0)
				keys.pop(0)

		film_json['title'] = title
		film_json['forreign_title'] = foreign_title
		film_json['film_id'] = str(film_id)	
		
		return json.dumps(film_json, ensure_ascii=False).encode('utf8')

	def retrive_country(self, film_id):
		text = self.load_film(film_id)
		soup = BeautifulSoup(text)
		
		if text is None:
			return None
		film_country = soup.find('table', {'class': 'info'})
		country_td = film_country.find_all('tr')[1].find_all('td')[1]
		country = country_td.find_all('a')[0].get_text()
		return country

	def cache_page(self, page_content, filename):
		import codecs
		if self.from_cache:
			with open('cache/films/{0}.htm'.format(filename), 'w') as fid:
				fid.write(page_content.encode('utf-8'))

	def check_cached_film(self, film_id):
		if self.from_cache == False:
			return False
		from os.path import exists
		if exists('cache/films/{0}.htm'.format(film_id)):
			return True
		return False

	def get_cached_film(self, film_id):
		import codecs
		with codecs.open('cache/films/{0}.htm'.format(film_id),'r') as f:
			return f.read()

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

	def close(self):
		self.selenium.close()



class ParserTop250Walls(KinopoiskParser):

	def __init__(self, from_cache, test_mode = False):
		KinopoiskParser.__init__(self, from_cache, test_mode)
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
				logger.info(TAG, 'film {0} not have wallpapers'.format(film.film_id))
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
		logger.info(TAG, 'save img url: {0}'.format(url))
		with open('cache/img_urls.txt', 'a') as the_file:
			the_file.write('{0}\n'.format(url))

	def setup_top_250_films_ids(self, film_ids_list = None):
		text = self.get_page_content(TOP_250)
		self.cache_page(text, 'top250')
		soup = BeautifulSoup(text)
		
		all_places = soup.find_all('tr', {'id':re.compile("top250_place_[0-9]")})
		#self.test_places(all_places)

		logger.info(TAG, 'Films count: {}'.format(len(all_places)))
		i = 0
		for place in all_places: #all_a[2:252]
			foreign_title = place.find('span', {'class': 'text-grey'})
			if foreign_title is not None:
				foreign_title = foreign_title.get_text()
			a = place.find('a', {'class': 'all'})

			film_id = a.get('href').replace('/', ' ').split(' ')[2]

			if film_ids_list is not None:
				if film_id not in film_ids_list:
					continue
			
			country = self.retrive_country(film_id)
			if country is None:
				continue
			film = Film(film_id, "", self.clear_film_title(a.text)
				, country.lower())
			if foreign_title is not None:
				film.is_eng = True
				film.foreign_title = foreign_title
			logger.info(TAG, 'film_id: {0}'.format(film.film_id))
			self.top_250_films.append(film)
			logger.info(TAG, 'film proceed: {0}'.format(i))
			#logger.info(TAG, str(a.text))
			i += 1

			if self.test_mode:
				if i == 2:
					break

		shuffle(self.top_250_films)
		arrange_films_to_db(self.top_250_films)

	def clear_film_title(self, title):
		arr = title.split()
		arr.remove(arr[len(arr) - 1])
		return ' '.join(arr)

	def save_img(self, url, film_id):	
		logger.info(TAG, 'save img url: {0}'.format(url))
		img_data = requests.get(url).content
		with open('cache/images/{0}_800x600.{1}'.format(film_id, IMG_FILE_FORMAT), 'wb') as handler:
			handler.write(img_data)

	def download_images(self):
		logger.info(TAG, 'self.top_250_films len: {0}'.format(len(self.top_250_films)))
		for film in self.top_250_films:
			text = self.load_film_wall(film.film_id)
			if text == None:
				logger.info(TAG, 'wall page is null')
				continue
			self.process_img(text, film)
		#self.selenium.close()

	def test_setup_all(self):
		for film in self.top_250_films:
			logger.info(TAG, film.film_id)

	def test_places(self, all_places):
		test_foreign_title = all_places[0].find('span', {'class': 'text-grey'}).get_text()
		test_a = all_places[0].find('a', {'class': 'all'})
		logger.info(TAG, test_foreign_title)
		logger.info(TAG, test_a.text)



