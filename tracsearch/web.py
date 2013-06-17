import urllib
from flask import Flask, render_template, request
from flask.helpers import send_from_directory
from jinja2 import escape
from pyelasticsearch import ElasticSearch



def run(config, run=True):

    appli = Flask('tracsearch', instance_relative_config=True)
    appli.root_path = '.'
    if config.has_section('sentry'):
        from raven.contrib.flask import Sentry
        sentry = Sentry(appli, dsn=config.get('sentry', 'dsn'))

    es = ElasticSearch(config.get('elasticsearch', 'url', 'http://127.0.0.1:9200/'))

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
        facets = ['status', 'reporter', 'owner', 'priority', 'cc', 'keywords',
                'component', '_type', 'author', 'path', 'domain']
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
                'from': from_,
                'size': size,
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
                query['facets']['changetime']['facet_filter'] = {'term': selected}

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
                query['facets']['changetime']['facet_filter'] = {'range': filter_}
                context['start'] = start
                context['end'] = end

            tmp = request.args.copy()
            tmp['from'] = int(request.args.get('from', 0)) + 1

            context['next'] = urllib.urlencode(tmp)
            print query
            context['from'] = from_
            context['size'] = size
            results = es.search(query, index='trac')
            print results['hits'].keys()
            context['results'] = results
        return render_template('index.html', **context)

    appli.debug = config.get('web', 'debug', False)
    if run:
        appli.run(config.get('web', 'host', '127.0.0.1'))
    else:
        return appli

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
