from flask import Flask
from flask_restplus import Api, Resource
from modules.appleId_check_db import ProfileExistence
from raven.contrib.flask import Sentry
from config import Config


app = Flask(__name__)
app.config["MONGO_URI"] = Config.MONGO_URI
app.config["SENTRY_DSN"] = Config.SENTRY_DSN
app.config["RESTPLUS_MASK_SWAGGER"] = False

api = Api(app, version='1.0', title='Apple Service')
search = api.namespace('search', description='Search endpoints')
sentry = Sentry(app)


@search.route('/id/<string:mail_id>')
@search.response(200, '{"data":{"availability": true, false}}')
class AppleIdChecker(Resource):
    @search.doc('email checker')
    def get(self, mail_id):
        """email checker"""
        obj = ProfileExistence()
        data = obj.db_check(mail_id)

        return {'data': {"availability": data['profileExists']}}


if __name__ == '__main__':
    app.run(port=5000)
