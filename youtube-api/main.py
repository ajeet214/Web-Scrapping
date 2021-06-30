from flask import Flask, jsonify
from flask_restplus import Api, Resource, reqparse
from modules.youtube_db import PostSearch
from raven.contrib.flask import Sentry
from config import Config

app = Flask(__name__)

app.config["MONGO_URI"] = Config.MONGO_URI
app.config["SENTRY_DSN"] = Config.SENTRY_DSN
app.config["RESTPLUS_MASK_SWAGGER"] = False

api = Api(app, version='1.0', title='Youtube Service')
search = api.namespace('search', description='Search endpoints')
sentry = Sentry(app)

search_filter = reqparse.RequestParser()
search_filter.add_argument('q', type=str, help='search string', required=True)


@search.route('')
class YoutubeSearch(Resource):
    @search.doc('youtube search')
    @search.expect(search_filter, validate=True)
    def get(self):
        """youtube search"""
        args = search_filter.parse_args()
        obj = PostSearch()

        output = obj.db_check(args['q'])
        return jsonify(output)


if __name__ == '__main__':
    app.run(port=5000)


