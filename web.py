from ConfigParser import ConfigParser

from flask import Flask, render_template, request
from flask.helpers import send_from_directory
from pyelasticsearch import ElasticSearch

from trac import Trac


config = ConfigParser()
config.read(['tracsearch.ini'])

app = Flask(__name__)
es = ElasticSearch(config.get('elasticsearch', 'url', 'http://127.0.0.1:9200/'))
trac = Trac(config.get('trac', 'url', 'http://robert:password@127.0.0.1/trac'))


@app.route("/components/<path:filename>")
def components(filename):
    return send_from_directory("components", filename)


@app.route("/", methods=['GET'])
def hello():
    q = request.args.get('q', '')
    if q == '':
        results = None
    else:
        # http://www.elasticsearch.org/guide/reference/query-dsl/query-string-query.html
        query = {
            'query': {
                'query_string': {
                    'query': q
                }
            },
            'sort': [
                {'changetime': 'desc'}
            ],
            'facets': {
                'status': {
                    'terms': {'field': 'status'}
                },
                'reporter': {
                    'terms': {'field': 'reporter'}
                }
            },
            'highlight': {
                "pre_tags": ["<b>"],
                "post_tags": ["</b>"],
                'fields': {
                    '_all': {},
                    'comment.comment': {},
                    'description': {},
                    'summary': {}
                }
            }
        }
        results = es.search(query, index='trac')
    return render_template('index.html',
                           results=results,
                           q=q,
                           trac_root=trac.web)

app.debug = config.get('web', 'debug', False)

if __name__ == "__main__":
    app.run(config.get('web', 'host', '127.0.0.1'))
