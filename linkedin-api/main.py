from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields, reqparse
from modules.linkedinSearch_db import LinkedinSearch
from modules.linkedin_db import ProfileExistence
from modules.profile_db import ProfileFetch
from modules.group_search import GroupSearch
from modules.linkedin_search_pubsub import ProfileSearch
from modules.post_search import SearchClass
from modules.profile_posts import ProfilePosts
from modules.profile_article import ProfileArticles
from raven.contrib.flask import Sentry
from config import Config


app = Flask(__name__)
app.config["MONGO_URI"] = Config.MONGO_URI
app.config["SENTRY_DSN"] = Config.SENTRY_DSN
app.config["RESTPLUS_MASK_SWAGGER"] = False

api = Api(app, version='1.0', title='Linkedin Service')

linkedin_service = api.namespace('', description='linkedin_service endpoints')

profile = api.namespace('profile', description='profiles endpoints')

search = api.namespace('search', description='Search endpoints')

sentry = Sentry(app)


# profile search filter
search_filter = reqparse.RequestParser()
search_filter.add_argument('q', type=str, help='search string', required=True)
search_filter.add_argument('language', type=str, help='ISO 2 Letter Language Codes like en, fr')
search_filter.add_argument('region', type=str, help='alpha 2 country code like us, in')
search_filter.add_argument('company', type=str, help='target company name')
search_filter.add_argument('title', type=str, help='software engineer')


@search.route('/profiles')
@search.response(500, '{"message": "no data found"}')
@search.response(200, '{"channel_id": "linkedin_profile_search0x7fb5324268d0>"}')
class LinkedinProfileSearchRoute(Resource):
    '''Shows list profiles based on query and  other filters'''
    @search.doc('profile search')
    @search.expect(search_filter, validate=True)
    def get(self):
        '''linkedin profile search'''
        args = search_filter.parse_args()
        print(args)
        obj = ProfileSearch()

        response = obj.search(q=args['q'], region=args['region'], company=args['company'],
                         title=args['title'], language=args['language'])

        print(response)
        try:
            if response['message']:
                return response, 500
        except KeyError:
            return response


# profile fetcher-------------------------------------------------------------------------------------------------
@profile.route('/<string:username>')
class LinkedinProfileRoute(Resource):

    @profile.doc('profile fetch')
    def get(self, username):
        '''linkedin profile fetch'''
        obj = ProfileFetch()
        response = obj.db_check(username)

        return response


# email checker---------------------------------------------------------------------------------------------------
@linkedin_service.route('/id/<string:mail_id>')
@linkedin_service.response(200, '{"data":{"availability": true, false}}')
class EmailChecker(Resource):

    def get(self, mail_id):
        '''email checker'''
        obj1 = ProfileExistence()
        data = obj1.db_check(mail_id)
        return {'data': {'availability': data['profileExists']}}


# group search----------------------------------------------------------------------------------------------------

# group search filter
group_search_filter = reqparse.RequestParser()
group_search_filter.add_argument('q', type=str, help='search string', required=True)


@search.route('/groups')
@search.response(500, '{"message": "no data found"}')
@search.response(200, '{"channel_id": "linkedin_group_search0x7fb5324268d0>"}')
class LinkrdinGroupSearch(Resource):

    @search.expect(group_search_filter, validate=True)
    def get(self):
        '''linkedin group search'''
        args = group_search_filter.parse_args()
        obj1 = GroupSearch()
        response = obj1.search(args['q'])
        print(response)
        try:
            if response['message']:
                return response, 500
        except KeyError:
            return response, 200


# post search-----------------------------------------------------------------------------------------------------

# post search filter
post_search_filter = reqparse.RequestParser()
post_search_filter.add_argument('q', type=str, help='search string', required=True)
post_search_filter.add_argument('time_duration', type=str, help='date filter', choices=(
    'past_day', 'past_week', 'past_month'))


@search.route('/posts')
@search.response(500, '{"message": "data not found"}')
@search.response(200, '{"channel_id": "linkedin_post_search0x7fb5324268d0>"}')
class LinkedinPostSearch(Resource):

    @search.expect(post_search_filter, validate=True)
    def get(self):
        '''linkedin post search'''
        args = post_search_filter.parse_args()
        obj1 = SearchClass()
        response = obj1.search(q=args['q'], time_duration=args['time_duration'])
        print(response)

        try:
            if response['message']:
                return response, 500
        except KeyError:
            return response, 200


# profile posts --------------------------------------------------------------------------------------------------
@profile.route('/posts/<string:username>/<string:category>')
@search.response(500, '{"message": "data not found"}')
@search.response(200, "{'channel_id': 'profile_posts_object at 0x163b468>'}")
class ProfilePostsRoute(Resource):

    @profile.doc('profile posts')
    def get(self, username, category):
        '''linkedin profile posts'''
        obj = ProfilePosts(username=username, category=category)
        response = obj.processor()

        try:
            if response['message']:
                return response, 500
        except KeyError:
            return response, 200


# profile articles --------------------------------------------------------------------------------------------------
@profile.route('/articles/<string:username>')
@search.response(500, '{"message": "data not found"}')
@search.response(200, "{'channel_id': 'profile_articles_object at 0x1105f88>'}")
class ProfileArticlesRoute(Resource):

    @profile.doc('profile articles')
    def get(self, username):
        '''linkedin profile articles'''
        obj = ProfileArticles(username=username)
        response = obj.processor()

        try:
            if response['message']:
                return response, 500
        except KeyError:
            return response, 200


if __name__ == '__main__':
    app.run(debug=True)
