#!/usr/bin/env python

from trac import Trac
from search import TracSearch, datetimeformat
from ConfigParser import ConfigParser
from StringIO import StringIO

config = ConfigParser()
config.read(['tracsearch.ini'])
trac = Trac(config.get('trac', 'url', None))
search = TracSearch(
    config.get('elasticsearch', 'url', 'http://127.0.0.1:9200'),
    bulk_size=config.getint('elasticsearch', 'bulk_size')
)


def unCamel(txt):
    "Split cameled word."
    txt = unicode(txt)
    r = StringIO()
    first = True
    for l in range(len(txt) - 1):
        if not first and txt[l].isupper() and txt[l + 1].islower():
            r.write(u" ")
        r.write(txt[l])
        first = False
    r.write(txt[-1])
    return r.getvalue()

for wiki in trac.wiki():
    wiki['id'] = wiki['name']
    path = wiki['name'].split('/')
    wiki['name'] = u" / ".join([unCamel(w) for w in path])
    print wiki['name']
    if len(path) > 1:
        wiki['path'] = []
        for a in range(1, len(path)):
            wiki['path'].append('/'.join(path[:a]))
        print wiki['path']
    wiki['changetime'] = datetimeformat(wiki['lastModified'])
    search.index('wiki', wiki, bulk=True)

search.flush_bulk('wiki')
