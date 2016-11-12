import os

#default config
class BaseConfig(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


#other child config inheriting the BaseConfig,and override some config maybe
