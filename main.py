#!/usr/bin/env python

from if3py.parsers.kinopoisk import ParserTop250Walls

# 1. get list of 250 films
# 2. get from each film its film id
# 3. get img_url from film id

parser = ParserTop250Walls(from_cache = False)
parser.setup_top_250_films_ids()
#parser.test_setup_all()
parser.setup_all()
