#!/usr/bin/env python

import os, glob
import subprocess
from random import randint
from if3py.utils import logger 

TAG = 'TORCH_STYLIZE'

class TorchStylize:

	def __init__(self):
		self.init_workspace()

	def init_workspace(self):
		models_dir = os.getcwd() + '/torch/models'
		if not os.path.exists(models_dir):
			os.makedirs(models_dir)

		self.act_dir = os.getcwd() + '/torch/'

		self.work_dir = os.getcwd()
		os.chdir(self.act_dir + 'models')

		self.models = [m for m in glob.glob("*.t7")]

		logger.info(TAG, self.models)
		logger.info(TAG, len(self.models))

		self.lua_script = 'fast_neural_style.lua'

		if not os.path.exists(self.lua_script):
			logger.info(TAG, 'Please put {0} to folder {1}'.format(self.lua_script, self.act_dir))

	def get_random_model(self):
		rnd_index = randint(0,len(self.models) - 1)
		return self.models[rnd_index]

	def stylize_image_with_torch(self, in_image, out_image, img_size = 802, model = None):
		os.chdir(self.act_dir)
		if model is None:
			model = self.get_random_model()
		subprocess.call(["th", self.lua_script,
						'-model', 'models/{}'.format(model),
						'-image_size', str(img_size),
						 '-input_image', self.work_dir + '/' + in_image,
						 '-output_image', self.work_dir + '/' + out_image])

		os.chdir(self.work_dir)