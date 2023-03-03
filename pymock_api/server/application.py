from abc import ABCMeta, abstractmethod


class BaseAppServer(metaclass=ABCMeta):
    @abstractmethod
    def setup(self):
        pass


class FlaskServer(BaseAppServer):
    def setup(self):
        from flask import Flask

        app: Flask = Flask(__name__)
        return app
