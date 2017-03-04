#!/usr/bin/env python
# -*- coding: utf-8 -*-

import PIL
from PIL import Image

def scale(image_name, factor):
	pass

def resize(image_in, image_out, basewidth = 500):
	img = Image.open(image_in)
	wpercent = (basewidth/float(img.size[0]))
	hsize = int((float(img.size[1])*float(wpercent)))
	img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
	img.save(image_out) 

def crop_center(image_name, height, width):
	pass