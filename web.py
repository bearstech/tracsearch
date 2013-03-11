from ConfigParser import ConfigParser

from flask import Flask, render_template, request
from flask.helpers import send_from_directory
from jinja2 import escape
from pyelasticsearch import ElasticSearch

from trac import Trac


config = ConfigParser()
config.read(['tracsearch.ini'])

app = Flask(__name__)
es = ElasticSearch(config.get('elasticsearch', 'url', 'http://127.0.0.1:9200/'))
trac = Trac(config.get('trac', 'url', 'http://robert:password@127.0.0.1/trac'))


@app.template_filter('nicedate')
def nicedate(value):
    value = escape(value)
    year = value[0:4]
    month = value[4:6]
    day = value[6:8]
    time = value[9:17]
    return "%s-%s-%s %s" % (year, month, day, time)


@app.route("/components/<path:filename>")
def components(filename):
    return send_from_directory("components", filename)


@app.route("/", methods=['GET'])
def index():
    q = request.args.get('q', '')
    facets = ['status', 'reporter', 'owner', 'priority', 'cc', 'keywords', 'component']
    selected = {}
    for facet in facets:
        a = request.args.get('facet_%s' % facet, '')
        if a != '':
            selected[facet] = a
    facet_status = request.args.get('facet_status', '')
    facet_reporter = request.args.get('facet_reporter', '')
    if q == '':
        results = None
    else:
        # http://www.elasticsearch.org/guide/reference/query-dsl/query-string-query.html
        query = {
            'query': {
                'query_string': {
                    'query': q,
                    'default_operator': 'AND'
                }
            },
            'sort': [
                {'changetime': 'desc'}
            ],
            'facets': {},
            'highlight': {
                "pre_tags": ["<b>"],
                "post_tags": ["</b>"],
                'fields': {
                    '_all': {},
                    'comment.comment': {},
                    'description': {},
                    'summary': {}
                }
            },
            'filter': {}
        }
        for facet in facets:
            query['facets'][facet] = {
                'terms': {'field': facet}
            }
            if selected != {}:
                query['facets'][facet]['facet_filter'] = {'term': selected}

        if selected != {}:
            query['filter'] = {'term': selected}

        results = es.search(query, index='trac')
    return render_template('index.html',
                           results=results,
                           q=q,
                           trac_root=trac.web,
                           facets=selected)

app.debug = config.get('web', 'debug', False)

if __name__ == "__main__":
    app.run(config.get('web', 'host', '127.0.0.1'))
