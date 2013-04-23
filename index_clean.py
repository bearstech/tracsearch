#!/usr/bin/env python

from config import config
from search import TracSearch


search = TracSearch(config.get('elasticsearch', 'url', 'http://127.0.0.1:9200'))
search.recreate()
