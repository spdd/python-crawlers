#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import os.path

from if3py.utils import logger 
from if3py.utils.file import check_folder_and_create

TAG = 'BASE_SQLITE'

SQLITE_DB_EXT = 'sqlite'
DB_FILE_NAME = 'data'

DB_FOLDER = 'db'
CSV_OUTPUT_FOLDER = 'db/csv'

class SqliteManager:

	def __init__(self, lang = 'ru'):
		self.base_dir = os.getcwd()
		self.lang = lang
		logger.info(TAG, self.base_dir)

		check_folder_and_create(DB_FOLDER)
		check_folder_and_create(CSV_OUTPUT_FOLDER)

		db_path = os.path.join(self.base_dir, "{0}/{1}_{2}.{3}".format(DB_FOLDER, DB_FILE_NAME, lang, SQLITE_DB_EXT))

		self.con = lite.connect(db_path)
		with self.con:
			self.cur = self.con.cursor()
			self.create_db(self.con)
			self.cur.execute("SELECT * FROM puzzles")
		self.mLevel = 1
		self.level_pack_count = 40

	def create_db(self, conn):
		cur = conn.cursor()

		field_type_int = 'INTEGER'  # column data type
		field_type_text = 'TEXT'

		# levels table
		self.table_levels = 'levels'  
		col_table_levels_1 = '_id'
		col_table_levels_2 = 'level'
		col_table_levels_3 = 'puzzle_id'

		# puzzles table
		self.table_puzzles = 'puzzles' 
		col_table_puzzles_1 = '_id'
		col_table_puzzles_2 = 'letters'
		col_table_puzzles_3 = 'json'
		col_table_puzzles_4 = 'difficulty'

		cur.execute('CREATE TABLE IF NOT EXISTS {tn} ({nf1} {ft1}, {nf2} {ft2}, {nf3} {ft3}, PRIMARY KEY(_id))  '\
        	.format(tn=self.table_levels, \
        		nf1=col_table_levels_1, ft1=field_type_int,
        		nf2=col_table_levels_2, ft2=field_type_int,
        		nf3=col_table_levels_3, ft3=field_type_text
        		))

		cur.execute('CREATE TABLE IF NOT EXISTS {tn} ({nf1} {ft1}, {nf2} {ft2}, {nf3} {ft3}, {nf4} {ft4}, PRIMARY KEY(_id))  '\
        	.format(tn=self.table_puzzles, \
        		nf1=col_table_puzzles_1, ft1=field_type_text,
        		nf2=col_table_puzzles_2, ft2=field_type_text,
        		nf3=col_table_puzzles_3, ft3=field_type_text,
        		nf4=col_table_puzzles_4, ft4=field_type_int
        		))
		conn.commit()

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

	def export_to_csv(self):
		self.read_and_save(self.table_puzzles)
		self.read_and_save(self.table_levels)

	def read_and_save(self, table_name):
		import pandas.io.sql as sql
		import csv
		table = sql.read_sql_query('SELECT * FROM {0}'.format(table_name), self.con)
		table.to_csv('{0}/{1}_{2}.csv'.format(CSV_OUTPUT_FOLDER, table_name, self.lang),
		 encoding = 'utf-8', quotechar='"', quoting = csv.QUOTE_ALL, index = False)

	def close(self):
		self.con.close()
		self.cur.close()