#!/usr/bin/env python

from tracsearch.config import config
from tracsearch.search import TracSearch


search = TracSearch(config.get('elasticsearch', 'url', 'http://127.0.0.1:9200'))
search.recreate()
