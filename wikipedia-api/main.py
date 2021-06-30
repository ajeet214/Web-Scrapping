from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields, reqparse
from modules.wikipedia import Wikipedia
from raven.contrib.flask import Sentry
from config import Config


app = Flask(__name__)

app.config["MONGO_URI"] = Config.MONGO_URI
app.config["SENTRY_DSN"] = Config.SENTRY_DSN
app.config["RESTPLUS_MASK_SWAGGER"] = False

api = Api(app, version='1.0', title='Wikipedia Service')
search = api.namespace('search', description='Search endpoints')
sentry = Sentry(app)

search_filter = reqparse.RequestParser()
search_filter.add_argument('q', type=str, help='search string', required=True)
search_filter.add_argument('limit', type=str, help='number of results limit')


@search.route('')
class WikipediaSearch(Resource):
    @search.doc('wikipedia search')
    @search.expect(search_filter, validate=True)
    def get(self):
        """wikipedia search"""
        args = search_filter.parse_args()
        obj = Wikipedia()

        output = obj.processor(args['q'], args['limit'])
        return jsonify(output)


if __name__ == '__main__':
    app.run(debug=True, port=5000)

