from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError


class Search(object):
    def __init__(self, index,  url, bulk_size=100):
        self._index = index
        self.es = ElasticSearch(url)
        self._bulk = {}
        self.bulk_size = bulk_size

    def delete(self):
        try:
            assert self.es.delete_index(self._index)['ok']
        except ElasticHttpNotFoundError:
            pass

    def create(self):
        self.es.create_index(self._index)

    def recreate(self):
        self.delete()
        self.create()

    def flush(self):
        self.es.refresh(self._index)

    def index(self, table, value, bulk=False):
        if not bulk:
            self.es.index(self._index, table, value)
            return
        if table not in self._bulk:
            self._bulk[table] = []
        self._bulk[table].append(value)
        if len(self._bulk[table]) > self.bulk_size:
            self.flush_bulk(table, flush=False)

    def flush_bulk(self, table, flush=True):
        if len(self._bulk[table]):
            self.es.bulk_index(self._index, table, self._bulk[table])
            self._bulk[table] = []
            if flush:
                self.flush()


class TracSearch(Search):
    def __init__(self, url, bulk_size=100):
        super(TracSearch, self).__init__('trac', url, bulk_size)

    def create(self):
        super(TracSearch, self).create()
        mapping = {
            'name': {
                'boost': 1.0,
                'index': 'analyzed',
                'store': 'yes',
                'type': 'string',
                "term_vector": "with_positions_offsets"
            },
        }
        self.es.put_mapping(self._index, "wiki", {'properties': mapping})
        mapping = {
                'ticket': {
                    '_all': {
                        'enabled': True
                        },
                    'properties': {
                        'description': {
                            'type': 'string',
                            'store': 'yes',
                            "term_vector": "with_positions_offsets"
                            },
                        'summary': {
                            'boost': 2.0,
                            'type': 'string',
                            'store': 'yes',
                            "term_vector": "with_positions_offsets"
                            }
                        },
                        'comment': {
                            'type': 'nested',
                            'include_in_parent': True
                        },
                        'changetime': {
                            'type': 'date',
                            'store': 'yes'
                        }
                    }
                }
        self.es.put_mapping(self._index, "ticket", mapping)
        mapping = {
                'comment': {
                    '_parent': {'type': 'ticket'},
                    'properties': {}
                    }
                }
        self.es.put_mapping(self._index, "comment", mapping)
