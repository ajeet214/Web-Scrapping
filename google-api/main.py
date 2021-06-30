from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields, reqparse
from modules.googleNews import GoogleNews
from modules.googleVideo import GoogleVideo
from modules.googleSearch import GoogleSearch
from modules.google_db import Google_db
from modules.knowledge_graph_search import KnowledgeGraphSearch
from modules.google_contacts import GoogleContacts
from config import Config


from raven.contrib.flask import Sentry

app = Flask(__name__)
app.config["MONGO_URI"] = Config.MONGO_URI
app.config["SENTRY_DSN"] = Config.SENTRY_DSN
app.config["RESTPLUS_MASK_SWAGGER"] = False

api = Api(app, version='1.0', title='Google Service')

search = api.namespace('search', description='Search endpoints')

sentry = Sentry(app)

# ---------------------------google web search------------------------------------------------
# search filter
search_filter = reqparse.RequestParser()
search_filter.add_argument('q', type=str, help='search string', required=True)
search_filter.add_argument('exclude', type=str, help='word to exclude')
search_filter.add_argument('site', type=str, help='forbes.com')
search_filter.add_argument('intitle', type=str, help='word to find in search title')
search_filter.add_argument('filetype', type=str, help='file type filter', choices=('pdf', 'xls', 'ppt', 'doc'))
search_filter.add_argument('time_duration', type=str, help='date filter', choices=('past_day', 'past_week', 'past_month', 'past_year'))
search_filter.add_argument('from_date', type=int, help=1552322834)
search_filter.add_argument('to_date', type=int, help=1552322834)


@search.route('')
@search.response(500, '{"message": "no data found,", "captcha detected"}')
@search.response(200, '{"channel_id": "google_web_service_183e6139328a96d31e6e64b65f65dd78"}')
class GoogleSearchRoute(Resource):
    '''Shows list of web search results based on query and  other filters'''
    @search.doc('web search')
    @search.expect(search_filter, validate=True)
    def get(self):
        '''google web search'''
        args = search_filter.parse_args()
        print(args)
        obj = GoogleSearch()

        res = obj.processor(q=args['q'], filetype=args['filetype'], site=args['site'],
                            time_duration=args['time_duration'], exclude=args['exclude'], intitle=args['intitle'])

        print(res)
        try:
            if res['message']:
                return res, 500
        except KeyError:
            return res, 200
# -------------------------------------------google news search ------------------------------


# news filter
news_filter = reqparse.RequestParser()
news_filter.add_argument('q', type=str, help='search string', required=True)
news_filter.add_argument('exclude', type=str, help='word to exclude')
news_filter.add_argument('site', type=str, help='forbes.com')
news_filter.add_argument('intitle', type=str, help='word to find in search title')
news_filter.add_argument('time_duration', type=str, help='date filter', choices=('past_day', 'past_week', 'past_month', 'past_year'))
news_filter.add_argument('from_date', type=int, help=1552322834)
news_filter.add_argument('to_date', type=int, help=1552322834)


@search.route('/news')
@search.response(500, '{"message": "no data found,", "captcha detected"}')
@search.response(200, '{"channel_id": "google_news_service_183e6139328a96d31e6e64b65f65dd78"}')
class GoogleSearchNews(Resource):
    """Shows list of news search results based on query and  other filters"""
    @search.doc('news search')
    @search.expect(news_filter, validate=True)
    def get(self):
        """google news search"""
        args = news_filter.parse_args()
        print(args)
        obj = GoogleNews()

        res = obj.processor(q=args['q'], site=args['site'],
                            time_duration=args['time_duration'], exclude=args['exclude'], intitle=args['intitle'])

        print(res)
        try:
            if res['message']:
                return res, 500
        except KeyError:
            return res, 200
# -----------------------------------google video search -------------------------------------


# video filter
video_filter = reqparse.RequestParser()
video_filter.add_argument('q', type=str, help='search string', required=True)
video_filter.add_argument('exclude', type=str, help='word to exclude')
video_filter.add_argument('site', type=str, help='forbes.com')
video_filter.add_argument('intitle', type=str, help='word to find in search title')
video_filter.add_argument('time_duration', type=str, help='date filter', choices=('past_day', 'past_week', 'past_month', 'past_year'))
video_filter.add_argument('from_date', type=int, help=1552322834)
video_filter.add_argument('to_date', type=int, help=1552322834)


@search.route('/videos')
@search.response(500, '{"message": "no data found,", "captcha detected"}')
@search.response(200, '{"channel_id": "google_video_service_183e6139328a96d31e6e64b65f65dd78"}')
class GoogleSearchVideo(Resource):
    """Shows list of video search results based on query and  other filters"""
    @search.doc('video search')
    @search.expect(video_filter, validate=True)
    def get(self):
        """google video search"""
        args = news_filter.parse_args()
        print(args)
        obj = GoogleVideo()

        res = obj.processor(q=args['q'], site=args['site'],
                            time_duration=args['time_duration'], exclude=args['exclude'], intitle=args['intitle'])

        print(res)
        try:
            if res['message']:
                return res, 500
        except KeyError:
            return res, 200
# ---------------------------------------------------------------------------------------


# model for knowledge search
knowledge_model = api.model('Knowledge Search', {
    'content': fields.String(readOnly=True),
    'description': fields.String(readOnly=True),
    'id': fields.String(readOnly=True),
    'image_url': fields.String(readOnly=True),
    'profile_image': fields.String(readOnly=True),
    'profile_name': fields.String(readOnly=True),
    'profile_url': fields.String(readOnly=True),
    'polarity': fields.String(readOnly=True, description='sentiment polarity of content', example='positive, negative, neutral'),
    'linked_url': fields.String(readOnly=True),
    'score': fields.Float(readOnly=True),
})

data = api.model('', {'data': fields.List(fields.Nested(knowledge_model))})

# knowledge filter
knowledge_filter = reqparse.RequestParser()
knowledge_filter.add_argument('q', type=str, help='search string', required=True)
knowledge_filter.add_argument('limit', type=int, help='count')


@search.route('/knowledge-graph')
@search.response(500, '{"message": "limit exceeded", "no data found"}')
class GoogleKnowledgeSearch(Resource):
    @search.doc('knowledge search')
    @search.expect(knowledge_filter, validate=True)
    @search.marshal_with(data)
    def get(self):
        """google knowledge search"""
        args = knowledge_filter.parse_args()
        obj = KnowledgeGraphSearch()
        # query = request.args.get('q')
        # limit = request.args.get('limit')
        if not args['limit']:
            args['limit'] = 20
        result = obj.processor(args['q'], limit=args['limit'])
        # return jsonify(result)
        try:
            if result['message']:
                return result, 500
        except KeyError:
            return result


# @app.route('/api/v1/google_contacts', methods=['POST', 'GET'])
@search.route('/google_contacts')
class GoogleContacts(Resource):
    def post(self):
        global request_data
        if request.method == 'POST':
            request_data = request.get_json()
            # numbers = request_data['number_list']

        obj = GoogleContacts()
        res = obj.checker(request_data)
        return jsonify({"data": res})


@search.route('/id/<string:mail_id>')
@search.response(200, '{"data":{"availability": true, false}}')
class EmailChecker(Resource):
    @search.doc('email checker')
    def get(self, mail_id):
        """email checker"""
        # email = request.args.get('email_id')
        obj = Google_db()
        data_db = obj.db_check(mail_id)
        # print(data_db)
        # obj = EmailChecker()
        # data = obj.checker(email)
        # obj2.data_loader(data)
        try:
            # return jsonify({'result': data_db})
            # return jsonify({'data': {"availability": data_db['email']}})
            return {'data': {"availability": data_db['email']}}

        except TypeError:
            data = dict()
            data['name'] = data_db['name']
            data['email'] = data_db['email']
            data['image'] = data_db['image']
            data['googlePlusId'] = data_db['googlePlusId']
            data['email_id'] = data_db['email_id']
            # return jsonify({'result': data})
            # return jsonify({'data': {"availability": data['email']}})
            return {'data': {"availability": data['email']}}


if __name__ == '__main__':
    app.run(debug=True)

