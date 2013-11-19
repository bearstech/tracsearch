import urllib
import logging
from flask import Flask, render_template, request
from flask.helpers import send_from_directory
from jinja2 import escape

logger = logging.getLogger('elasticsearch')
logger.addHandler(logging.StreamHandler())

from elasticsearch import Elasticsearch


def run(config, run=True):

    appli = Flask('tracsearch', instance_relative_config=True)
    appli.root_path = '.'
    if config.has_section('sentry'):
        from raven.contrib.flask import Sentry
        sentry = Sentry(appli, dsn=config.get('sentry', 'dsn'))

    if config.has_section('statsd'):
        from statsd import StatsClient
        stats = StatsClient(config.get('statsd', 'host'), 8125, prefix='tracsearch')
    else:
        stats = None

    es = Elasticsearch(hosts=config.get('elasticsearch', 'url', '127.0.0.1:9200'))


    @appli.template_filter('nicedate')
    def nicedate(value):
        value = escape(value)
        year = value[0:4]
        month = value[4:6]
        day = value[6:8]
        time = value[9:17]
        return "%s-%s-%s %s" % (year, month, day, time)

    @appli.route("/components/<path:filename>")
    def components(filename):
        return send_from_directory("components", filename)

    @appli.route("/", methods=['GET'])
    def index():
        q = request.args.get('q', '')
        size = 20
        from_ = int(request.args.get('from', 0))
        facets = ['status', 'user', 'priority', 'keywords',
                  'component', '_type', 'path', 'domain']
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
                'filter': {},
            }
            for facet in facets:
                query['facets'][facet] = {
                    'terms': {'field': facet}
                }
                if selected != {}:
                    query['facets'][facet]['facet_filter'] = {'term': selected}

            if selected != {}:
                query['filter'] = {'term': selected}
                query['facets']['changetime']['facet_filter'] = {'term':
                                                                 selected}

            context = dict(q=q, facets=selected)
            start = request.args.get('start', '')
            end = request.args.get('end', '')
            if end != '':
                filter_ = {'changetime': {
                    'from': int(start),
                    'to': int(end)
                }
                }
                query['filter']['range'] = filter_
                query['facets']['changetime']['facet_filter'] = {'range':
                                                                 filter_}
                context['start'] = start
                context['end'] = end

            tmp = request.args.copy()
            tmp['from'] = int(request.args.get('from', 0)) + 1
            context['next'] = urllib.urlencode(encode_dict(tmp))
            tmp['from'] = tmp['from'] - 2
            context['previous'] = urllib.urlencode(encode_dict(tmp))
            tmp['from'] = 0
            context['first'] = urllib.urlencode(encode_dict(tmp))
            print query
            context['from'] = from_
            context['size'] = size
            results = es.search(
                index='trac', size=size, body=query
            )
            if stats:
                stats.incr('query')
                stats.timing('query', results['took'])
            print results.keys()
            print results['hits']
            context['results'] = results
        return render_template('index.html', **context)

    appli.debug = config.get('web', 'debug', False)
    if run:
        appli.run(config.get('web', 'host', '127.0.0.1'))
    else:
        return appli


# http://stackoverflow.com/questions/6480723/urllib-urlencode-doesnt-like-unicode-values-how-about-this-workaround
def encode_dict(map):
    return dict([(key, val.encode('utf-8')) for key, val in map.items()
                 if isinstance(val, basestring)])

_app = None


def app(environ, start_response):
    import os
    from tracsearch.config import config
    global _app
    if _app is None:
        conf = os.getenv('TRACSEARCH_CONF')
        if conf is None:
            conf = "tracsearch.ini"
        config.read([conf])
        _app = run(config, run=False)
    return _app(environ, start_response)
