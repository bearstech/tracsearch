#!/usr/bin/env python

import datetime

from config import config
from trac import Trac
from search import TracSearch, datetimeformat


search = TracSearch(
    config.get('elasticsearch', 'url', 'http://127.0.0.1:9200'),
    bulk_size=config.getint('elasticsearch', 'bulk_size')
)
for t in config.tracs():
    trac = Trac(config.get(t, 'url', None))

    period = datetime.timedelta(config.getint(t, 'ticket_timedelta'))

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
