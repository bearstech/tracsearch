#!/usr/bin/env python

from ConfigParser import ConfigParser
from search import Search


config = ConfigParser()
config.read(['tracsearch.ini'])
search = Search(config.get('elasticsearch', 'url', 'http://127.0.0.1:9200'))
search.recreate()
