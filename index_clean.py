#!/usr/bin/env python

from ConfigParser import ConfigParser
from search import TracSearch


config = ConfigParser()
config.read(['tracsearch.ini'])
search = TracSearch(config.get('elasticsearch', 'url', 'http://127.0.0.1:9200'))
search.recreate()
