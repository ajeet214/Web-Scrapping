from flask import Flask, jsonify
from flask_restplus import Api, Resource, fields, reqparse
from raven.contrib.flask import Sentry
from modules.bing_web_search import BingSearch
from modules.bing_news_search import BingNewsSearch
from modules.bing_videos_search import BingVideosSearch
from config import Config


app = Flask(__name__)
# api = Api(app, title='Bing')
app.config["MONGO_URI"] = Config.MONGO_URI
app.config["SENTRY_DSN"] = Config.SENTRY_DSN
app.config["RESTPLUS_MASK_SWAGGER"] = False

api = Api(app, title='Bing Service')
search = api.namespace('search', description='Search Endpoints')
sentry = Sentry(app)

# ------------------------bing web search--------------------------------------------------------------

# web search filter
web_search_filter = reqparse.RequestParser()
web_search_filter.add_argument('q', type=str, help='search string')
web_search_filter.add_argument('exclude', type=str, help='word to exclude in search string')
web_search_filter.add_argument('site', type=str, help='bbc.com')
web_search_filter.add_argument('filetype', type=str, help='file type filter', choices=('pdf', 'xls', 'ppt', 'doc'))
web_search_filter.add_argument('from_date', type=int, help='1430926269')
web_search_filter.add_argument('to_date', type=int, help='1530926269')
web_search_filter.add_argument('time_duration', type=str, help='date filter', choices=('past_day', 'past_week',
                                                                                       'past_month', 'past_year'))


@search.route('')
@search.response(500, "{'message': 'no data found'}")
@search.response(200, '{"channel_id": "bing_web_service_183e6139328a96d31e6e64b65f65dd78"}')
class BingWeb(Resource):
    @search.expect(web_search_filter, validate=True)
    def get(self):
        '''bing web search'''
        args = web_search_filter.parse_args()
        obj = BingSearch()
        response = obj.processor(q=args['q'], exclude=args['exclude'], site=args['site'],
                                 filetype=args['filetype'], from_date=args['from_date'],
                                 to_date=args['to_date'], time_duration=args['time_duration'], )

        print(response)
        try:
            if response['message']:
                return response, 500
        except KeyError:
            return response, 200
# ----------------------------------bing news search--------------------------------------------------


# news search filter
news_search_filter = reqparse.RequestParser()
news_search_filter.add_argument('q', type=str, help='search string')
news_search_filter.add_argument('exclude', type=str, help='word to exclude in search string')
news_search_filter.add_argument('site', type=str, help='bbc.com')
news_search_filter.add_argument('time_duration', type=str, help='date filter', choices=('past_hour', 'past_day',
                                                                                        'past_week', 'past_month'))


@search.route('/news')
@search.response(500, "{'message': 'no data found'}")
@search.response(200, '{"channel_id": "bing_news_service_183e6139328a96d31e6e64b65f65dd78"}')
class BingNews(Resource):
    @search.expect(news_search_filter, validate=True)
    def get(self):
        '''bing news search'''
        args = news_search_filter.parse_args()
        obj = BingNewsSearch()
        response = obj.processor(q=args['q'], exclude=args['exclude'], site=args['site'],
                                 time_duration=args['time_duration'], )

        print(response)
        try:
            if response['message']:
                return response, 500
        except KeyError:
            return response, 200
# -----------------------------------bing videos search-----------------------------------------------


# videos search filter
videos_search_filter = reqparse.RequestParser()
videos_search_filter.add_argument('q', type=str, help='search string')
videos_search_filter.add_argument('exclude', type=str, help='word to exclude in search string')
videos_search_filter.add_argument('site', type=str, help='bbc.com')
videos_search_filter.add_argument('time_duration', type=str, help='date filter', choices=('past_day', 'past_week',
                                                                                          'past_month', 'past_year'))


@search.route('/videos')
@search.response(500, "{'message': 'no data found'}")
@search.response(200, '{"channel_id": "bing_videos_service_183e6139328a96d31e6e64b65f65dd78"}')
class BingVideos(Resource):
    @search.expect(videos_search_filter, validate=True)
    def get(self):
        '''bing videos search'''
        args = videos_search_filter.parse_args()
        obj = BingVideosSearch()
        response = obj.processor(q=args['q'], exclude=args['exclude'], site=args['site'],
                                 time_duration=args['time_duration'], )

        print(response)
        try:
            if response['message']:
                return response, 500
        except KeyError:
            return response, 200


if __name__ == '__main__':
    app.run(debug=True)
