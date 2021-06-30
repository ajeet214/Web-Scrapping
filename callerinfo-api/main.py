from flask import Flask, request, jsonify
from modules.callerInfo_db import CallerInfo
from raven.contrib.flask import Sentry

#create the Flask app
app = Flask(__name__)
sentry = Sentry(app)


@app.route('/api/v1/search')
def number_fetch():
    number = request.args.get('number')  # if key doesn't exist, returns None
    obj = CallerInfo()
    data = obj.db_check(number)
    return jsonify({'data': data})


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5012)
