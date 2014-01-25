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

    def test_dummy(self):
        self.trac.index('ticket', [{'plop': 42}])
        self.trac.refresh()
        res = self.trac.es.search(index='ticket', body={"query":
                                                        {"match_all": {}}})
        hits = res['hits']['hits']
        assert len(hits) == 1
        assert hits[0]['_source']['plop'] == 42
