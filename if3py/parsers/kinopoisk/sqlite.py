#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

from if3py.data.sqlite import SqliteManager
from if3py.utils import logger 

TAG = 'KINOPOISK_SQLITE'

langs = ['ru', 'en']

def arrange_films_to_db(films):
	en_films = []
	for film in films:
		if film.is_eng:
			en_films.append(film)

	# update/insert rus films
	db_ru = KinopoiskDB()
	db_ru.process_films(films)

	# update/insert foreign films
	db_en = KinopoiskDB('en')
	db_en.process_films(en_films)


class KinopoiskDB(SqliteManager):
	def __init__(self, lang = 'ru'):
		base_dir = os.getcwd()
		SqliteManager.__init__(self, base_dir, lang)
		self.level_pack_count = 40

	def createJson(self, film):
		resultString = '{ "max_length_word": "2", "words_count": "1",' 
		resultString += '"word1":"%s",' % self.get_film_title(film).lower()
		resultString += '"country":"%s",' % film.country
		resultString += '"film_id":"%s" }' % film.film_id
		return resultString

	def get_film_title(self, film):
		if self.lang == 'ru':
			return film.title
		else:
			return film.foreign_title

	def transform_title(self, title):
		return title \
			.replace('«', '') \
			.replace('»','') \
			.replace('...', '') \
			.replace('!', '')	\
			.replace('№', '')	\
			.replace(':', '')	\
			.replace('-', ' ')

	def process_films(self, films):
		i = 1
		for film in films:
			json = self.createJson(film)
			row = self.cur.fetchone()
			if row == None:
				self.insert_puzzle(i, self.get_film_title(film), json, 0)
				logger.info(TAG, 'insert {0} film with lang {1}'.format(i, self.lang))
			else:
				self.update_puzzle(self.get_film_title(film), json, 0, row[0])
				logger.info(TAG, 'update {0} film with lang {1}'.format(i, self.lang))
			self.update_levels(row, i)
			i=i+1

	def update_country(self, film_id, country):
		c = self.con.cursor()
		c.execute("SELECT * FROM puzzles")
		parsed_string = None
		row = 1
		while row is not None:
			row = c.fetchone()
			parsed_string = json.loads(row[2])
			if parsed_string['film_id'] == film_id:
				parsed_string['country'] = country
				result = json.dumps(parsed_string, ensure_ascii=False).encode('utf8')
				self.update_puzzle(row[1], str(result), 0, row[0])
				break
		logger.info(TAG, 'film not found')
		c.close()