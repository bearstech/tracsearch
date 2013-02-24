from pyes import ES
import json


class Search(object):
    def __init__(self):
        self.conn = ES('127.0.0.1:9200', encoder=json.JSONEncoder)
        self.index = self.conn.index

    def delete(self):
        try:
            self.conn.indices.delete_index("trac")
        except:
            pass

    def create(self):
        self.conn.indices.create_index("trac")
        mapping = {
            'name': {
                'boost': 1.0,
                'index': 'analyzed',
                'store': 'yes',
                'type': 'string',
                "term_vector": "with_positions_offsets"
            },
        }
        self.conn.indices.put_mapping("wiki", {'properties': mapping}, ["trac"])
        self.conn.indices.put_mapping("ticket", {'properties': mapping}, ["trac"])

    def recreate(self):
        self.delete()
        self.create()

    def flush(self):
        self.conn.flush_bulk()
        self.conn.indices.refresh("trac")
