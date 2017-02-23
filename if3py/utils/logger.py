#!/usr/bin/env python

import logging

LOG_LEVEL = logging.INFO # logging.WARNING

def check_config():
	logging.basicConfig(format='%(levelname)s:%(message)s', level=LOG_LEVEL)

def info(msg):
	check_config()
	#print(msg)
	logging.info(msg)

def warning(msg):
	check_config()
	logging.warning(msg)