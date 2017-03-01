#!/usr/bin/env python

import os, glob
from if3py.data.sqlite import SqliteManager
from if3py.parsers.kinopoisk import KinopoiskParser
from random import shuffle

work_dir = os.getcwd()
os.chdir('cache/images/stylized')
images_names = [i.replace('.jpg', '') for i in [m for m in glob.glob("*.jpg")]]
shuffle(images_names)

print(images_names)
print(len(images_names))

os.chdir(work_dir)

parser = KinopoiskParser()

for _id in images_names:
	sqlite = SqliteManager()
	country = parser.retrive_country(_id)
	sqlite.update_country(_id, country)
parser.close()