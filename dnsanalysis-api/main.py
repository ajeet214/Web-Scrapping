from flask import Flask, jsonify, request
from modules.lookups import Lookups
from modules.scrap_lookup import ScrapLookup
from raven.contrib.flask import Sentry

app = Flask(__name__)
sentry = Sentry(app)


@app.route('/api/v1/lookup')
def lookup_with_api():
    obj = Lookups()
    lookup_type = request.args.get('command')
    domain_name = request.args.get('domain')
    response = obj.lookups(lookup_type, domain_name)
    return jsonify(response)


@app.route('/api/v1/lookups')
def lookup_with_selenium():
    obj = ScrapLookup()
    lookup_type = request.args.get('command')
    domain_name = request.args.get('domain')
    response = obj.check_pickle(lookup_type, domain_name)
    return jsonify(response)


if __name__ == '__main__':

    app.run(port=5015)
