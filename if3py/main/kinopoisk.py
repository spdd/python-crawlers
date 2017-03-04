#!/usr/bin/env python
# -*- coding: utf-8 -*-

from if3py.parsers.kinopoisk.kinopoisk import KinopoiskParser, ParserTop250Walls, IMG_FILE_FORMAT
from if3py.ml.image.torch.stylize import TorchStylize
from if3py.data.sqlite import SqliteManager, SQLITE_DB_EXT, DB_FOLDER
from if3py.utils import logger 
from if3py.utils.file import check_folder_and_create
from if3py.utils.image import resize

import os, glob
from random import shuffle

# 1. get list of 250 films
# 2. get from each film its film id
# 3. get img_url from film id

TAG = 'KINOPOISK_MAIN'

RESULT_IMAGES_FOLDER = 'stylized'
DOWLOADED_IMAGES_FOLDER = 'cache/images/'
FULL_STYLIZED_IMAGES_PATH = '{0}{1}'.format(DOWLOADED_IMAGES_FOLDER, RESULT_IMAGES_FOLDER)
RESIZED_IMAGES_FOLDER = 'cache/images/resized'

PRIMARY_TORCH_MODEL = 'mosaic.t7'
STYLIZED_IMG_SIZE = 1002

class KinopoiskMain:

	def __init__(self, test_mode = False):
		self.test_mode = test_mode
		self.work_dir = os.getcwd()
		check_folder_and_create(FULL_STYLIZED_IMAGES_PATH)
		check_folder_and_create(RESIZED_IMAGES_FOLDER)

	def stylize_downloaded_images(self):
		os.chdir(DOWLOADED_IMAGES_FOLDER)
		images_names = [m for m in glob.glob("*.{}".format(IMG_FILE_FORMAT))]

		os.chdir(self.work_dir)

		torch = TorchStylize()

		for im in images_names:
			name = im.split('_')[0]
			out_name = name + '.{}'.format(IMG_FILE_FORMAT)

			torch.stylize_image_with_torch('{0}{1}'.format(DOWLOADED_IMAGES_FOLDER,im),
									'{0}/{1}'.format(FULL_STYLIZED_IMAGES_PATH, out_name),
									img_size = STYLIZED_IMG_SIZE, 
									model = PRIMARY_TORCH_MODEL)
			if self.test_mode:
				break
		os.chdir(self.work_dir)

	def get_stylized_images_names(self):
		os.chdir(FULL_STYLIZED_IMAGES_PATH)
		images_names = [i.replace('.{}'.format(IMG_FILE_FORMAT), '') for i in [m for m in glob.glob("*.{}".format(IMG_FILE_FORMAT))]]
		shuffle(images_names)

		logger.info(TAG, images_names)
		logger.info(TAG, len(images_names))

		os.chdir(self.work_dir)
		return images_names


	def parse_top250_films_save_to_db_and_save_images(self):
		parser = ParserTop250Walls(from_cache = False, test_mode = self.test_mode)
		parser.setup_top_250_films_ids()
		parser.download_images()

	def parse_top250_films_save_to_db(self):
		parser = ParserTop250Walls(from_cache = False, test_mode = self.test_mode)
		parser.setup_top_250_films_ids()

	def get_info_with_film_title(self, film_title):
		pass

	def get_info_with_film_id(self, film_id):
		parser = KinopoiskParser()
		json_str = parser.get_json_film_info_with_id(film_id)
		return json_str

	def clear_db(self):
		os.chdir(DB_FOLDER)
		db_names = [m for m in glob.glob("*.{}".format(SQLITE_DB_EXT))]
		logger.info(TAG, db_names)
		for db in db_names:
			os.remove(db)

		os.chdir(self.work_dir)

	def export_csv(self):
		self.export_csv_with_lang('ru')
		self.export_csv_with_lang('en')

	def export_csv_with_lang(self, lang):
		base_dir = os.getcwd()
		lite = SqliteManager(base_dir, lang)
		lite.export_to_csv()

	def resize(self, basewidth):
		os.chdir(FULL_STYLIZED_IMAGES_PATH)
		images = [i for i in glob.glob('*.{}'.format(IMG_FILE_FORMAT))]
		os.chdir(self.work_dir)

		for image in images:
			image_in = '{0}/{1}'.format(FULL_STYLIZED_IMAGES_PATH, image)
			image_out = '{0}/{1}'.format(RESIZED_IMAGES_FOLDER, image)
			resize(image_in, image_out, basewidth)
			logger.info(TAG, image_out)
			if self.test_mode:
				break

		logger.info(TAG, 'Success resized {} images'.format(len(images)))



