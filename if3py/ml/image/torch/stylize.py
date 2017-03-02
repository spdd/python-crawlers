#!/usr/bin/env python

import os, glob
import subprocess
from random import randint
from if3py.utils import logger 

TAG = 'TORCH_STYLIZE'

models_dir = os.getcwd() + '/torch/models'
if not os.path.exists(models_dir):
	os.makedirs(models_dir)

act_dir = os.getcwd() + '/torch/'

work_dir = os.getcwd()
os.chdir(act_dir + 'models')

models = [m for m in glob.glob("*.t7")]

logger.info(TAG, models)
logger.info(TAG, len(models))

lua_script = 'fast_neural_style.lua'

if not os.path.exists(lua_script):
	logger.info(TAG, 'Please put {0} to folder {1}'.format(lua_script, act_dir))

def get_random_model():
	rnd_index = randint(0,len(models) - 1)
	return models[rnd_index]

def stylize_image_with_torch(in_image, out_image, img_size = 802, model = None):
	os.chdir(act_dir)
	if model is None:
		model = get_random_model()
	subprocess.call(["th", lua_script,
					'-model', 'models/{}'.format(model),
					'-image_size', str(img_size),
					 '-input_image', work_dir + '/' + in_image,
					 '-output_image', work_dir + '/' + out_image])


os.chdir(work_dir)