from flask import Flask, jsonify, request
from raven.contrib.flask import Sentry
from modules.reddit_db import PostSearch


app = Flask(__name__)
sentry = Sentry(app)

"""
    possible stype values
    blog
    url
    site
    -------
    subblog
    username
    selftext
"""


# @app.route('/api/v1/search/<string:type>/<string:query>')
@app.route('/api/v1/search')
def search():
    query = request.args.get('q')
    post_type = request.args.get('type')
    reddit = PostSearch()
    response = reddit.db_check(query, post_type)
    return jsonify(response)


if __name__ == '__main__':
    app.run(port=5016)
