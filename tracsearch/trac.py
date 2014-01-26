from urlparse import urlparse
from xml.parsers.expat import ExpatError
import xmlrpclib
import datetime
from StringIO import StringIO


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


class Trac(object):

    def __init__(self, url):
        uri = "%s/trac/rpc" % url
        p = urlparse(uri)
        self.web = "%s://%s" % (p.scheme, p.hostname)
        self.trac = xmlrpclib.ServerProxy(uri)
        self.hostname = p.hostname

    def wiki(self):
        for page in self.trac.wiki.getAllPages():
            info = self.trac.wiki.getPageInfo(page)
            try:
                body = self.trac.wiki.getPage(page)
            except:
                body = ''
                print "Oups sur la page %s" % info['name']
            path = info['name'].split('/')
            data = {'id': info['name'],
                    'title': u" / ".join([unCamel(w) for w in path]),
                    'user': info['author'],
                    'version': info['version'],
                    'lastModified': info['lastModified'].value,
                    'body': body,
                    'domain': self.hostname,
                    'url': "%s/trac/wiki/%s" % (self.web, info['name'])
                    }
            if len(path) > 1:
                data['path'] = []
                for a in range(1, len(path)):
                    data['path'].append('/'.join(path[:a]))
            yield data

    def ticket(self, since):
        today = datetime.datetime.today()
        for t in self.trac.ticket.getRecentChanges(today - since):
            try:
                id_, created, changed, attributes = self.trac.ticket.get(t)
                attributes['id'] = id_
                #attributes['created'] = created
                #attributes['changed'] = changed
                attributes['cc'] = attributes['cc'].split(', ')
                for k in ['time', 'changetime']:
                    attributes[k] = attributes[k].value
                attributes['id'] = str(attributes['id'])
                attributes['domain'] = self.hostname
                attributes['url'] = "%s/trac/ticket/%s" % (self.web, attributes['id'])
                comments = []
                for time, author, field, oldvalue, newvalue, permanent in self.trac.ticket.changeLog(t):
                    if field == 'comment':
                        comments.append({'user': author, 'time': time.value, 'comment': newvalue})
                attributes['user'] = set()
                attributes['user'].add(attributes['owner'])
                for cc in attributes['cc']:
                    if cc:
                        attributes['user'].add(cc)
                attributes['user'] = list(attributes['user'])
                attributes['title'] = attributes['summary']
                del attributes['summary']
                yield attributes, comments
            except ExpatError:  # xml trouble
                print "Crash while fetching %s" % t
