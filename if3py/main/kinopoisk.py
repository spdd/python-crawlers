#!/usr/bin/env python
# -*- coding: utf-8 -*-

from if3py.parsers.kinopoisk.kinopoisk import ParserTop250Walls
from if3py.ml.image.torch.stylize import TorchStylize
from if3py.utils import logger 

import os, glob
from random import shuffle

# 1. get list of 250 films
# 2. get from each film its film id
# 3. get img_url from film id

TAG = 'KINOPOISK_MAIN'

class KinopoiskMain:

	def __init__(self, test_mode = False):
		self.test_mode = test_mode
		self.work_dir = os.getcwd()
		self.check_folders()

	def check_folders(self):
		cache_dir_path = os.path.join(self.work_dir, 'cache/images/stylized')
		if not os.path.exists(cache_dir_path):
			os.makedirs(cache_dir_path)

	def stylize_downloaded_images(self):
		os.chdir('cache/images')
		images_names = [m for m in glob.glob("*.jpg")]

		os.chdir(self.work_dir)

		torch = TorchStylize()

		for im in images_names:
			name = im.split('_')[0]
			out_name = name + '.jpg'

			torch.stylize_image_with_torch('cache/images/{}'.format(im),
									'cache/images/stylized/{}'.format(out_name),
									img_size = 1002, 
									model = 'mosaic.t7')
		os.chdir(self.work_dir)

	def get_stylized_images_names(self):
		os.chdir('cache/images/stylized')
		images_names = [i.replace('.jpg', '') for i in [m for m in glob.glob("*.jpg")]]
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
		pass

	def clear_db(self):
		os.chdir('db')
		db_names = [m for m in glob.glob("*.db")]
		logger.info(TAG, db_names)
		for db in db_names:
			os.remove(db)

		os.chdir(self.work_dir)


