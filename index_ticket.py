#!/usr/bin/env python

import datetime
from ConfigParser import ConfigParser

from trac import Trac
from search import Search


config = ConfigParser()
config.read(['tracsearch.ini'])
trac = Trac(config.get('trac', 'url', None))
search = Search(config.get('elasticsearch', 'url', 'http://127.0.0.1:9200'))

period = datetime.timedelta(int(config.get('index:ticket', 'timedelta', 30)))
bulk_tickets = []
for ticket, comments in trac.ticket(period):
    print ticket['summary']
    ticket['comment'] = []
    n = 0
    for comment in comments:
        comment['id'] = "%s_%i" % (ticket['id'], n)
        ticket['comment'].append(comment)
        n += 1
    bulk_tickets.append(ticket)
search.es.bulk_index('trac', 'ticket', bulk_tickets)
search.flush()
