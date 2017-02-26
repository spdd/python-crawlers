#!/usr/bin/env python

import os, glob
import subprocess
from random import randint

act_dir = os.getcwd() + '/if3py/ml/image/torch/'

work_dir = os.getcwd()
os.chdir(act_dir + 'models')
models = [m for m in glob.glob("*.t7")]

print(models)
print(len(models))

lua_script = 'fast_neural_style.lua'

def get_random_model():
	rnd_index = randint(0,len(models) - 1)
	return models[rnd_index]

def stylize_image_with_torch(in_image, out_image):
	os.chdir(act_dir)
	model = get_random_model()
	subprocess.call(["th", lua_script,
					'-model', 'models/{}'.format(model),
					'-image_size', '802',
					 '-input_image', work_dir + '/' + in_image,
					 '-output_image', work_dir + '/' + out_image])


os.chdir(work_dir)