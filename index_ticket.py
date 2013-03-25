#!/usr/bin/env python

import datetime
from ConfigParser import ConfigParser

from trac import Trac
from search import TracSearch


config = ConfigParser()
config.read(['tracsearch.ini'])
trac = Trac(config.get('trac', 'url', None))
search = TracSearch(
    config.get('elasticsearch', 'url', 'http://127.0.0.1:9200'),
    bulk_size=config.getint('elasticsearch', 'bulk_size')
)

period = datetime.timedelta(config.getint('index:ticket', 'timedelta'))


def datetimeformat(raw):
    raw = str(raw)
    return "%s-%s-%sT%s" % (raw[0:4], raw[4:6], raw[6:8], raw[9:])

for ticket, comments in trac.ticket(period):
    print ticket['summary']
    ticket['comment'] = []
    ticket['changetime'] = datetimeformat(ticket['changetime'])
    n = 0
    for comment in comments:
        comment['id'] = "%s_%i" % (ticket['id'], n)
        ticket['comment'].append(comment)
        n += 1
    search.index('ticket', ticket, bulk=True)

search.flush_bulk('ticket')
