import os


class Config:

    DATABASE_CONFIG = {
        'host': os.environ.get('MONGO_HOST', 'localhost'),
        'port': os.environ.get('MONGO_PORT', 27017)
    }

    SELENIUM_CONFIG = {
        'host': os.environ.get('SELENIUM_HOST', 'localhost'),
        'port': str(os.environ.get('SELENIUM_PORT', 4444))
    }
