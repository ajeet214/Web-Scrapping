import os


class Config:

    MONGO_URI = os.environ.get("MONGO_URI", default="127.0.0.1:27017")

    SELENIUM_URI = os.environ.get("SELENIUM_URI", default="http://localhost:4444/wd/hub")

    SENTRY_DSN = os.environ.get("SENTRY_DSN", default="")