#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import os.path
import json

from if3py.utils import logger 

class SqliteManager:

	def __init__(self):
		BASE_DIR = os.path.dirname(os.path.abspath(__file__))
		db_path = os.path.join(BASE_DIR, "data.db")
		self.con = lite.connect(db_path)
		with self.con:
			self.cur = self.con.cursor()
			self.cur.execute("SELECT * FROM puzzles")
		self.mLevel = 1
		self. level_pack_count = 40

	def insertPuzzle(self, count, match, json, size):
		self.con.execute("INSERT INTO puzzles VALUES(?, ?, ?, ?)", ('p' + str(count), match, json, size))
		self.con.commit()

	def updatePuzzle(self, match, json, size, row_id):
		self.con.execute("UPDATE puzzles SET letters=?, json=?, difficulty=? WHERE _id=?", (match, json, size, row_id))
		self.con.commit()

	def createJson(self, film):
		resultString = '{ "max_length_word": "2", "words_count": "1",' 
		resultString += '"word1":"%s",' % film.name
		resultString += '"country":"%s",' % film.country
		resultString += '"film_id":"%s" }' % film.film_id
		return resultString

	def processFilms(self, films):
		i = 1
		for film in films:
			json = self.createJson(film)
			row = self.cur.fetchone()
			if row == None:
				self.insertPuzzle(i, film.name, json, 0)
			else:
				self.updatePuzzle(film.name, json, 0, row[0])
			self.update_levels(row, i)
			i=i+1

	def update_levels(self, row, count):
		if row == None:
			self.con.execute("INSERT INTO levels VALUES(?, ?, ?)", (count, self.mLevel, 'p' + str(count)))
			self.con.commit()
		else:
			self.con.execute("UPDATE levels SET level=?, puzzle_id=? WHERE _id=?", (self.mLevel, 'p' + str(count), count))
			self.con.commit()
		if count % self.level_pack_count == 0:
			self.mLevel += 1

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
				print(result)
				print(row[0])
				print(row[1])
				self.updatePuzzle(row[1], str(result), 0, row[0])
				break
		logger.info('film not found')
		c.close()
		

	def close(self):
		self.con.close()
		self.cur.close()