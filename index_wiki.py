#!/usr/bin/env python

from trac import Trac
from search import TracSearch, datetimeformat
from ConfigParser import ConfigParser


config = ConfigParser()
config.read(['tracsearch.ini'])
trac = Trac(config.get('trac', 'url', None))
search = TracSearch(
    config.get('elasticsearch', 'url', 'http://127.0.0.1:9200'),
    bulk_size=config.getint('elasticsearch', 'bulk_size')
)

for wiki in trac.wiki():
    print wiki['name']
    print wiki
    wiki['id'] = wiki['name']
    wiki['changetime'] = datetimeformat(wiki['lastModified'])
    search.index('wiki', wiki, bulk=True)

search.flush_bulk('wiki')
