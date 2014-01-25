# FIXME use elasticsearch, not pyelasticsearch
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


def datetimeformat(raw):
    raw = str(raw)
    return "%s-%s-%sT%s" % (raw[0:4], raw[4:6], raw[6:8], raw[9:])


class Search(object):
    def __init__(self, index, host, settings=None):
        self._index = index
        self.es = Elasticsearch(host=host)
        self._settings = settings

    def delete(self):
        try:
            assert self.es.delete_index(self._index)['ok']
        except ElasticHttpNotFoundError:
            pass

    def create(self):
        assert self.es.create_index(self._index, settings=self._settings)['ok']
        print self.es.get_settings(self._index)

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


class TracSearch(object):
    def __init__(self, es):
        assert es.ping()
        self.es = es
        self.types = dict(
            ticket = {
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

            comment = {
                'comment': {
                    '_parent': {'type': 'ticket'},
                    'properties': {}
                }
            },

            wiki = {
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
        for k, v in self.types.items():
            if not self.es.indices.exists(k):
                self.es.indices.create(index=k, body={
                    'mappings': v,
                    'settings': settings}
                )

    def purge(self):
        for indice in self.types:
            if self.es.indices.exists(indice):
                self.es.indices.delete(indice)

    def refresh(self):
        for indice in self.types:
            if self.es.indices.exists(indice):
                self.es.indices.refresh(indice)

    def index(self, table, values):
        bulk(self.es, _wrap_index(table, values))


def _wrap_index(table, values):
    for value in values:
        value['_index'] = table
        value['_type'] = table
        yield value

"""
class TracSearch(Search):
    def __init__(self, url, bulk_size=100):
        settings = {
            'settings': {
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
        }
        super(TracSearch, self).__init__('trac', host, settings=settings)

    def create(self):
        super(TracSearch, self).create()
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
                }
        self.es.put_mapping(self._index, "ticket", mapping)
        mapping = {
                'comment': {
                    '_parent': {'type': 'ticket'},
                    'properties': {}
                    }
                }
        self.es.put_mapping(self._index, "comment", mapping)
        mapping = {
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
  "                     },
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
        self.es.put_mapping(self._index, "wiki", mapping)
        """
