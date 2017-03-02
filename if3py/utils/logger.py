#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

LOG_LEVEL = logging.INFO # logging.WARNING

def check_config():
	logging.basicConfig(format='%(levelname)s:%(message)s', level=LOG_LEVEL)

def info(tag, msg):
	check_config()
	logging.info('D/{0}: {1}'.format(tag, msg))

def warning(tag, msg):
	check_config()
	logging.warning('W/{0}: {1}'.format(tag, msg))