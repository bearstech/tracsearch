from flask import Flask, render_template, request

from pyelasticsearch import ElasticSearch

app = Flask(__name__)
es = ElasticSearch('http://127.0.0.1:9200/')


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
            'highlight': {
                "pre_tags" : ["<b>"],
                "post_tags" : ["</b>"],
                'fields': {
                    '_all': {},
                    'comment': {},
                    'description': {}
                }
            }
        }
        results = es.search(query, index='trac')

    return render_template('index.html', results=results)

app.debug = True

if __name__ == "__main__":
    app.run()
