from unittest import TestCase

from elasticsearch import Elasticsearch

from tracsearch.search import TracSearch


class SearchTest(TestCase):

    def setUp(self):
        es = Elasticsearch()
        self.trac = TracSearch(es)
        self.trac.purge()
        self.trac.indices()

    def test_dummy(self):
        self.trac.index('ticket', [{'plop': 42}])

