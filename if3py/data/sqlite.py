#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import os.path
import json

from if3py.utils import logger 

class SqliteManager:

	def __init__(self, base_dir, lang = 'ru'):
		self.lang = lang
		print(base_dir)
		db_path = os.path.join(base_dir, "db/data_{0}.db".format(lang))
		self.con = lite.connect(db_path)
		with self.con:
			self.cur = self.con.cursor()
			self.cur.execute("SELECT * FROM puzzles")
		self.mLevel = 1
		self.level_pack_count = 40

	def insert_puzzle(self, count, match, json, size):
		self.con.execute("INSERT INTO puzzles VALUES(?, ?, ?, ?)", ('p' + str(count), match, json, size))
		self.con.commit()

	def update_puzzle(self, match, json, size, row_id):
		self.con.execute("UPDATE puzzles SET letters=?, json=?, difficulty=? WHERE _id=?", (match, json, size, row_id))
		self.con.commit()

	def createJson(self, obj_):
		# should be override
		pass

	def update_levels(self, row, count):
		if row == None:
			self.con.execute("INSERT INTO levels VALUES(?, ?, ?)", (count, self.mLevel, 'p' + str(count)))
			self.con.commit()
		else:
			self.con.execute("UPDATE levels SET level=?, puzzle_id=? WHERE _id=?", (self.mLevel, 'p' + str(count), count))
			self.con.commit()
		if count % self.level_pack_count == 0:
			self.mLevel += 1

	def close(self):
		self.con.close()
		self.cur.close()