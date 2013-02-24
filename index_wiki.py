#!/usr/bin/env python

from trac import Trac
from search import Search

trac = Trac()
search = Search()

search.recreate()

for wiki in trac.wiki():
    print wiki['name']
    search.index(wiki, 'trac', 'wiki', id=wiki['name'], bulk=True)

search.flush()
