from ConfigParser import ConfigParser

from flask import Flask, render_template, request
from flask.helpers import send_from_directory
from jinja2 import escape
from pyelasticsearch import ElasticSearch

from trac import Trac


config = ConfigParser()
config.read(['tracsearch.ini'])
app = Flask(__name__)
if config.has_section('sentry'):
    from raven.contrib.flask import Sentry
    sentry = Sentry(app, dsn=config.get('sentry', 'dsn'))

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
    facets = ['status', 'reporter', 'owner', 'priority', 'cc', 'keywords', 'component', '_type', 'author']
    selected = {}
    for facet in facets:
        a = request.args.get('facet_%s' % facet, '')
        if a != '':
            selected[facet] = a
    if q == '':
        context = {'results': None}
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
            'facets': {
                'changetime': {
                    'date_histogram': {
                        'field': 'changetime',
                        'interval': 'week'
                    }
                }
            },
            'highlight': {
                "pre_tags": ["<b>"],
                "post_tags": ["</b>"],
                'fields': {
                    '_all': {},
                    'comment.comment': {},
                    'description': {},
                    'summary': {},
                    'body': {},
                    'name': {}
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
            query['facets']['changetime']['facet_filter'] = {'term': selected}

        context = dict(q=q,
                       trac_root=trac.web,
                       facets=selected)
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        if end != '':
            filter_ = {'changetime': {
                'from': int(start),
                'to': int(end)
            }
            }
            query['filter']['range'] = filter_
            query['facets']['changetime']['facet_filter'] = {'range': filter_}
            context['start'] = start
            context['end'] = end

        print query
        results = es.search(query, index='trac')
        print results
        context['results'] = results
    return render_template('index.html', **context)

app.debug = config.get('web', 'debug', False)

if __name__ == "__main__":
    app.run(config.get('web', 'host', '127.0.0.1'))
