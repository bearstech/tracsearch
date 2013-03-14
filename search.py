from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError


class Search(object):
    def __init__(self, url):
        self.es = ElasticSearch(url)

    def delete(self):
        try:
            assert self.es.delete_index("trac")['ok']
        except ElasticHttpNotFoundError:
            pass

    def create(self):
        self.es.create_index("trac")
        mapping = {
            'name': {
                'boost': 1.0,
                'index': 'analyzed',
                'store': 'yes',
                'type': 'string',
                "term_vector": "with_positions_offsets"
            },
        }
        self.es.put_mapping('trac', "wiki", {'properties': mapping})
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
        self.es.put_mapping("trac", "ticket", mapping)
        mapping = {
                'comment': {
                    '_parent': {'type': 'ticket'},
                    'properties': {}
                    }
                }
        self.es.put_mapping("trac", "comment", mapping)

    def recreate(self):
        self.delete()
        self.create()

    def flush(self):
        self.es.refresh("trac")
