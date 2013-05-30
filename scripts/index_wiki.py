#!/usr/bin/env python

from tracsearch.config import config
from tracsearch.trac import Trac
from tracsearch.search import TracSearch, datetimeformat

search = TracSearch(
    config.get('elasticsearch', 'url', 'http://127.0.0.1:9200'),
    bulk_size=config.getint('elasticsearch', 'bulk_size')
)
for t in config.tracs():
    trac = Trac(config.get(t, 'url', None))

    for wiki in trac.wiki():
        print wiki['name']
        wiki['changetime'] = datetimeformat(wiki['lastModified'])
        search.index('wiki', wiki, bulk=True)

    search.flush_bulk('wiki')
