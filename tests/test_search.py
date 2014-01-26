from unittest import TestCase

from elasticsearch import Elasticsearch

from tracsearch.search import TracSearch


class SearchTest(TestCase):

    def setUp(self):
        es = Elasticsearch()
        self.trac = TracSearch(es)
        assert self.trac.ping()
        self.trac.purge()
        self.trac.prepare_indices()
        self.trac.refresh()

    def test_dummy(self):
        self.trac.index('ticket', [{'plop': 42}])
        self.trac.refresh()
        res = self.trac.es.search(index='trac', body={"query":
                                                      {"match_all": {}}})
        hits = res['hits']['hits']
        assert len(hits) == 1
        assert hits[0]['_source']['plop'] == 42

    def test_search(self):
        self.trac.index('wiki', [
            {'name': 'Tracsearch',
             'body': 'Trachsearch is an useful search tool.'}])
        self.trac.refresh()
        res = self.trac.search('tool')
        assert res['hits']['total'] == 1
        hits = res['hits']['hits']
        assert len(hits) == 1
