from flask import Flask, jsonify, request
from modules.page_search_db import Db_processer
from modules.profile_search_db import Profile_db
from modules.Id_checker_db import Profile_existance
from modules.profile_fetch_db import ProfileFetchDb
from raven.contrib.flask import Sentry
from modules.fb_post_search import PostSearch
from modules.fb_post import PostSearch2

app = Flask(__name__)
sentry = Sentry(app)
# @app.route('/api/v1/profile/<string:profile>')
# def profile_fetch(profile):
#     f = ProfileFetch()
#     d = f.fb_profile_fetch(profile)
#     return jsonify(d)


@app.route('/api/v1/search/profile')
def profile_search():
    query = request.args.get('q')
    f = Profile_db()
    d = f.processor(query)
    print(d)
    return jsonify(d)


@app.route('/api/v1/profile')
def profile_fetch():
    query = request.args.get('id')
    f = ProfileFetchDb()
    d = f.db_check(query)
    return jsonify(d)


@app.route('/api/v1/search/page')
def page_search():
    query = request.args.get('q')
    f = Db_processer()
    d = f.processor(query)
    # print(d)
    return jsonify(d)

# @app.route('/api/v1/search/private/page/<string:search>')
# def private_page_search(search):
#     obj = PrivatePage()
#     func = obj.fb_pages(search)
#     return jsonify(func)

# @app.route('/api/v1/search/private/post/<string:search>')
# def private_post_search(search):
#     obj = PrivatePost()
#     func = obj.fb_post(search)
#     return jsonify(func)
#
# @app.route('/api/v1/search/private/profile/<string:search>')
# def private_profile_search(search):
#     obj = PrivateProfile()
#     func = obj.fb_profile(search)
#     return jsonify(func)

# @app.route('/api/v1/search')
# def email_checker():
#     email = request.args.get('mailid')  # if key doesn't exist, returns None
#     obj = EmailNumberChecker()
#     data = obj.fbEmailChecker(email)
#     return jsonify({'result': data})
#
#
# @app.route('/api/v1/search')
# def number_checker():
#     number = request.args.get('number')  # if key doesn't exist, returns None
#     obj = EmailNumberChecker()
#     data = obj.fbPhoneChecker(number)
#     return jsonify({'result': data})


# @app.route('/api/v1/search/id')
# def number_checker():
#     number = request.args.get('q')  # if key doesn't exist, returns None
#     obj = EmailNumberChecker()
#     data = obj.Checker(number)
#     return jsonify({'result': data})

@app.route('/api/v1/search/id')
def number_checker():
    number = request.args.get('q')  # if key doesn't exist, returns None
    # obj = EmailNumberChecker()
    # data = obj.Checker(number)
    obj1 = Profile_existance()
    data = obj1.db_check(number)
    return jsonify({'data': {"availability": data['profileExists']}})


@app.route('/api/v1/search/post')
def post_search():
    query = request.args.get('q')
    f = PostSearch()
    d = f.fb_posts(query)
    return jsonify({"data": d})

@app.route('/api/v1/post')
def fpost():
    query = request.args.get('q')
    f = PostSearch2()
    d = f.fb_posts(query)
    return jsonify({'client_id': d})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
