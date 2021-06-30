import os


class Config:

    MONGO_URI = os.environ.get("MONGO_URI", default="127.0.0.1:27017")

    SENTRY_DSN = os.environ.get("SENTRY_DSN", default="")

    SELENIUM_URI = os.environ.get("SELENIUM_URI", default="http://localhost:4444/wd/hub")

    REDIS_URI = os.environ.get("REDIS_URI", default="localhost:6379")

    MINIO_URI = os.environ.get("MINIO_URI", default="192.168.20.59:9090")
    MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", default="27FEF56C3C6E9E21")
    MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", default="AEF7F65C6562BCE3242ADF65B5788")
