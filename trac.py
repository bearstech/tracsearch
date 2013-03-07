import os
from urlparse import urlparse
import xmlrpclib
import datetime


class Trac(object):

    def __init__(self):
        uri = "%s/trac/rpc" % os.environ['TRAC_URL']
        p = urlparse(uri)
        self.web = "%s://%s" % (p.scheme, p.hostname)
        self.trac = xmlrpclib.ServerProxy(uri)

    def wiki(self):
        for page in self.trac.wiki.getAllPages():
            info = self.trac.wiki.getPageInfo(page)
            try:
                body = self.trac.wiki.getPageHTML(page)
            except:
                body = ''
                print "Oups sur la page %s" % info['name']
            data = {'name': info['name'],
                    'author': info['author'],
                    'version': info['version'],
                    'lastModified': info['lastModified'].value,
                    'body': body}
            yield data

    def ticket(self, since):
        today = datetime.datetime.today()
        for t in self.trac.ticket.getRecentChanges(today - since):
            id_, created, changed, attributes = self.trac.ticket.get(t)
            attributes['id'] = id_
            #attributes['created'] = created
            #attributes['changed'] = changed
            attributes['cc'] = attributes['cc'].split(', ')
            for k in ['time', 'changetime']:
                attributes[k] = attributes[k].value
            attributes['id'] = str(attributes['id'])
            comments = []
            try:
                for time, author, field, oldvalue, newvalue, permanent in self.trac.ticket.changeLog(t):
                    if field == 'comment':
                        comments.append({'author': author, 'time': time.value, 'comment': newvalue})
            except:  # xml trouble
                pass
            yield attributes, comments
