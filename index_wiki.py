#!/usr/bin/env python
import os
import xmlrpclib
from pyes import ES

conn = ES('127.0.0.1:9200')
try:
    conn.indices.delete_index("trac")
except:
    pass
conn.indices.create_index("trac")
mapping = {
    'name': {
        'boost': 1.0,
        'index': 'analyzed',
        'store': 'yes',
        'type': 'string',
        "term_vector": "with_positions_offsets"
    },
}
conn.indices.put_mapping("wiki", {'properties': mapping}, ["trac"])


uri = "%s/trac/rpc" % os.environ['TRAC_URL']
print uri
trac = xmlrpclib.ServerProxy(uri)
print trac.system.listMethods()
print trac.search.getSearchFilters()
for page in trac.wiki.getAllPages():
    info = trac.wiki.getPageInfo(page)
    #print dir(info['lastModified'])
    #print info['lastModified'].value
    print "\t", info['name']
    try:
        body = trac.wiki.getPageHTML(page)
    except:
        body = ''
        print "Oups sur la page %s" % info['name']
    conn.index({
        'name': info['name'],
        'author': info['author'],
        'version': info['version'],
        'lastModified': info['lastModified'].value,
        'body': body
    }, 'trac', 'wiki', bulk=True)
    #print trac.wiki.getPageHTML(page)

conn.flush_bulk()
conn.indices.refresh("trac")
