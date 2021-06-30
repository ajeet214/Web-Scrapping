from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields, reqparse
from raven.contrib.flask import Sentry
from modules.twitter_profile_search import TwitterSearch
# from modules.twitterprofile import ProfileClass
from modules.twittertweets import TwitterClass
from modules.twitter_friends_list import FriendsProfile
from modules.twitter_followers_list import FollowersProfile
from modules.trend import GeoTrend
from modules.profile_existence_db import ProfileExistence
from modules.twitter_profile_db import ProfileFetch
from config import Config

app = Flask(__name__)
app.config["MONGO_URI"] = Config.MONGO_URI
app.config["SENTRY_DSN"] = Config.SENTRY_DSN
app.config["RESTPLUS_MASK_SWAGGER"] = False

api = Api(app, title='Twitter Service')
search = api.namespace('search', description='Search Endpoints')
profile_endpoints = api.namespace('profile', description='Profile Endpoints')
other_endpoints = api.namespace('', description='Other Endpoints')
sentry = Sentry(app)

# ------------------------------------twitter search-------------------------------------------


# twitter search filter
search_filter = reqparse.RequestParser()
search_filter.add_argument('q', type=str, help='search string', required=True)
search_filter.add_argument('and_', type=str, help='word to search along wih q')
search_filter.add_argument('or_', type=str, help='word to search beside q')
search_filter.add_argument('exclude', type=str, help='word to exclude')
search_filter.add_argument('media', type=str, help='example: images/videos')
search_filter.add_argument('from_account', type=str, help='username')
search_filter.add_argument('hashtag', type=str, help='hashtags to search')
search_filter.add_argument('from_date', type=int, help='1461614174')
search_filter.add_argument('to_date', type=int, help='1561614174')
search_filter.add_argument('lang', type=str, help='alpha 2 language code like ru, en')
search_filter.add_argument('result_type', type=str, help='type of post', choices=('popular', 'recent', 'mixed'))
search_filter.add_argument('handle', type=str, help='handle to search')
search_filter.add_argument('to_account', type=str, help='username')


@search.route('')
@search.response(500, '{"message": "no data found"}')
@search.response(200, '{"channel_id": "twitter_search_service_0x7f30e0307080>>"}')
class SearchRoute(Resource):
    @search.doc('twitter search')
    @search.expect(search_filter, validate=True)
    def get(self):
        '''twitter search'''
        args = search_filter.parse_args()
        print(args)
        obj = TwitterClass()

        response = obj.processor(q=args['q'], and_=args['and_'], or_=args['or_'], exclude=args['exclude'],
                                 media=args['media'], from_account=args['from_account'], hashtag=args['hashtag'],
                                 from_date=args['from_date'], to_date=args['to_date'], lang=args['lang'],
                                 result_type=args['result_type'], handle=args['handle'], to_account=args['to_account'])

        print(response)
        try:
            if response['message']:
                return response, 500
        except KeyError:
            return response, 200
# ----------------------------twitter profile search------------------------


profile_search_filter = reqparse.RequestParser()
profile_search_filter.add_argument('q', type=str, help='search string', required=True)


@search.route('/profiles')
@search.response(500, '{"message": "no data found"}')
@search.response(200, '{"channel_id": "twitter_profile_search_service_<built-inmethodrandomofRandomobjectat0x1b21f68>"}')
class ProfileSearch(Resource):
    @search.expect(profile_search_filter, validate=True)
    def get(self):
        '''profile search'''
        args = profile_search_filter.parse_args()
        Obj = TwitterSearch()
        # limit = request.args.get('limit')
        response = Obj.profilesearch(args['q'])

        print(response)
        try:
            if response['message']:
                return response, 500
        except KeyError:
            return response, 200

# --------------------------------profile fetcher----------------------------


response_fields = api.model('profile fetch', {
    'description': fields.String(readOnly=True, description='brief description about the profile'),
    'profile_created_at': fields.Integer(readOnly=True, description='date in unix timestamp', example=1237380398),
    'name': fields.String(readOnly=True, description='name of the user'),
    'favourites_count': fields.Integer(readOnly=True),
    'screen_name': fields.String(readOnly=True, description='username'),
    'linked_urls': fields.String(readOnly=True, description='list of linked urls'),
    'followers_count': fields.Integer(readOnly=True, description='number of followers'),
    'profile_url': fields.String(readOnly=True, example="https://twitter.com/realdonaldtrump"),
    'polarity': fields.String(readOnly=True, example="postitve or negative or neutral"),
    'profile_banner_url': fields.String(readOnly=True),
    'profile_image_url': fields.String(readOnly=True),
    'type': fields.String(readOnly=True, example='identity'),
    "statuses_count": fields.Integer(readOnly=True),
    "location": fields.String(readOnly=True, description='location of profile'),
    "friends_count": fields.Integer(readOnly=True, description='no. of following'),
    "verified": fields.Boolean(readOnly=True)
})
data1 = api.model('profile fetch model', {
    "data": fields.Nested(response_fields)
})


@profile_endpoints.route('/<string:username>')
class ProfileFetchRoute(Resource):
    @profile_endpoints.marshal_with(data1)
    @profile_endpoints.doc('profile fetch')
    def get(self, username):
        '''twitter profile fetch'''
        obj = ProfileFetch()
        response = obj.db_check(username)

        return response
# ------------------------------friend/following profile ----------------------------


@profile_endpoints.route('/friends/<string:username>')
@profile_endpoints.response(500, "{'message': 'no data found'/'Max retries exceeded'}")
@profile_endpoints.response(200, '{"channel_id": "twitter_friend_profile_<built-inmethodrandomofRandomobjectat0x20dbd48>"}')
class FriendsProfileRoute(Resource):
    # @profile_endpoints.marshal_with(data)
    @profile_endpoints.doc('profile\'s friend')
    def get(self, username):
        '''list of friends profiles'''
        obj = FriendsProfile()
        response = obj.friendsprofile(username)

        try:
            if response['message']:
                return response, 500
        except KeyError:
            return response, 200

# ------------------------------followers profile ----------------------------


@profile_endpoints.route('/followers/<string:username>')
@profile_endpoints.response(500, "{'message': 'no data found'/'Max retries exceeded'}")
@profile_endpoints.response(200, '{"channel_id": "twitter_followers_profile_<built-inmethodrandomofRandomobjectat0x2aa9e48>"}')
class FollowersProfileRoute(Resource):
    # @profile_endpoints.marshal_with(data)
    @profile_endpoints.doc('profile\'s followers')
    def get(self, username):
        '''list of followers profiles'''
        obj = FollowersProfile()
        response = obj.followersprofile(username)

        try:
            if response['message']:
                return response, 500
        except KeyError:
            return response, 200


# -------------------------------email checker-------------------------------
@other_endpoints.route('/id/<string:mail_id>')
@other_endpoints.response(200, '{"data":{"availability": true, false}}')
class EmailChecker(Resource):

    def get(self, mail_id):
        '''email checker'''
        obj1 = ProfileExistence()
        response = obj1.db_check(mail_id)
        return {'data': {'availability': response['profileExists']}}

#
# # @app.route('/api/v1/profile/tweets/<string:tweets>')
# # @app.route('/api/v1/profile/tweets/<string:tweets>/<int:limit>')
# @app.route('/api/v1/profile/tweets')
# def profile_tweets():
#     query = request.args.get('q')
#     limit = request.args.get('limit')
#     i = TwitterClass()
#     result4 = i.profiletweets(query, limit)
#     return jsonify({'data': result4})
#
#
# # @app.route('/api/v1/tweets/hastag/<string:htag>')
# # @app.route('/api/v1/tweets/hastag/<string:htag>/<int:limit>')
# @app.route('/api/v1/tweets/hashtag')
# def tweets_hashtag():
#     query = request.args.get('q')
#     limit = request.args.get('limit')
#     j = TwitterClass()
#     result5 = j.hashtags(query, limit)
#     return jsonify({'data': result5})
#
#
# # @app.route('/api/v1/tweets/handle/<string:handler>')
# # @app.route('/api/v1/tweets/handle/<string:handler>/<int:limit>')
# @app.route('/api/v1/tweets/handle')
# def tweets_handle():
#     query = request.args.get('q')
#     limit = request.args.get('limit')
#     k = TwitterClass()
#     result6 = k.handlertweets(query, limit)
#     return jsonify({'data': result6})
#

# -------------------------trend search---------------------


# model for trend search
trend_model = api.model('Trend Search', {
    'name': fields.String(readOnly=True),
    'url': fields.String(readOnly=True),
    'promoted_content': fields.String(readOnly=True),
    'query': fields.String(readOnly=True),
    'tweet_volume': fields.String(readOnly=True),
})

data3 = api.model('twitter trend model', {'data': fields.List(fields.Nested(trend_model))})


trend_search_filter = reqparse.RequestParser()
trend_search_filter.add_argument('area_name', type=str, help='search string', required=True)


@search.route('/trend')
class TrendSearch(Resource):
    @search.doc('trend search')
    @search.marshal_with(data3)
    @search.expect(trend_search_filter, validate=True)
    def get(self):
        '''trend search'''
        args = trend_search_filter.parse_args()

        obj = GeoTrend()
        response = obj.geoStream(area_name=args['area_name'])
        return response


if __name__ == '__main__':
    app.run(debug=True)
