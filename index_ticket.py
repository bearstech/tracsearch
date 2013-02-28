#!/usr/bin/env python

import datetime
from trac import Trac
from search import Search


trac = Trac()
search = Search()
search.recreate()

period = datetime.timedelta(30)
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
