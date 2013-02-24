import os
import xmlrpclib
import datetime


class Trac(object):

    def __init__(self):
        uri = "%s/trac/rpc" % os.environ['TRAC_URL']
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
                  'body': body }
            yield data

    def ticket(self, since):
        today = datetime.datetime.today()
        for t in self.trac.ticket.getRecentChanges(today - since):
            id_, created, changed, attributes = self.trac.ticket.get(t)
            yield attributes

