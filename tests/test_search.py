from unittest import TestCase

from tracsearch.search import TracSearch


class SearchTest(TestCase):

    def setUp(self):
        self.trac = TracSearch('localhost:9200')
        self.trac.recreate()

    def test_dummy(self):
        self.trac.index('ticket', {'plop': 42})

