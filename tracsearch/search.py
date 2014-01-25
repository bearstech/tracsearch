# FIXME use elasticsearch, not pyelasticsearch
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


def datetimeformat(raw):
    raw = str(raw)
    return "%s-%s-%sT%s" % (raw[0:4], raw[4:6], raw[6:8], raw[9:])


class TracSearch(object):
    def __init__(self, es):
        self.es = es
        self.types = dict(
            ticket={
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
                        'url': {
                            'type': 'string',
                            'store': 'yes',
                            'index': 'no'
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
            },
            comment={
                'comment': {
                    '_parent': {'type': 'ticket'},
                    'properties': {}
                }
            },
            wiki={
                'wiki': {
                    '_all': {
                        'enabled': True
                    },
                    'properties': {
                        'changetime': {
                            'type': 'date',
                            'store': 'yes'
                        },
                        'body': {
                            'type': 'string',
                            'store': 'yes',
                            'analyzer': 'myHTML'
                        },
                        'name': {
                            'boost': 5.0,
                            'store': 'yes',
                            'type': 'string',
                            "term_vector": "with_positions_offsets"
                        },
                        'path': {
                            'type': 'string'
                        },
                        'url': {
                            'type': 'string',
                            'store': 'yes',
                            'index': 'no'
                        },
                    }
                }
            }
        )

    def ping(self):
        return self.es.ping()

    def prepare_indices(self):
        settings = {
            'analysis': {
                'analyzer': {
                    'myHTML': {
                        'type': 'custom',
                        'tokenizer': 'lowercase',
                        'char_filter': ['html_strip']
                    }
                }
            }
        }
        if not self.es.indices.exists('trac'):
            self.es.indices.create(index='trac', body={
                'mappings': self.types,
                'settings': settings}
            )

    def purge(self):
        if self.es.indices.exists('trac'):
            self.es.indices.delete('trac')

    def refresh(self):
        self.es.indices.refresh('trac')

    def index(self, table, values):
        bulk(self.es, _wrap_index(table, values))


def _wrap_index(table, values):
    for value in values:
        value['_index'] = 'trac'
        value['_type'] = table
        yield value
