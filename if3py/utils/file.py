#!/usr/bin/env python

import os

def check_folder_and_create(folder):
	work_dir = os.getcwd() # dir that run script
	dir_path = os.path.join(work_dir, folder)
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)