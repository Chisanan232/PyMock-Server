"""*The wrapper of application which ruled by SGI (server gateway interface)*

The factory to generate SGI application instance to run Python web framework.
"""

from abc import ABCMeta, abstractmethod


class BaseSGI(metaclass=ABCMeta):
    """*Base class of SGI*"""

    @classmethod
    @abstractmethod
    def server(cls):
        """Initial and set up an application via SGI application.

        Returns:
            An object which is SGI application.

        """
        pass


class WSGI(BaseSGI):
    """*WSGI application*

    This module for generating WSGI (Web Server Gateway Interface) application by Python tool *gunicorn*.
    """

    @classmethod
    def server(cls):
        from gunicorn.app.wsgiapp import WSGIApplication

        return WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]")
