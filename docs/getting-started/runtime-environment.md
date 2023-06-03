# Getting started

Actually, **_PyMock-API_** is a Python package which provides command line tool. So it still needs to install a Python
package to activate the command line feature.

## Runtime environment

**_PyMock-API_** only supports _Python 3.8 and newer_ version.

**_PyMock-API_** is a Python package which base on some giants to design and develop. It's obvious at the option ``--app-type``
which acceptable values are ``flask`` or ``fastapi``. In the other words, the code base depends on these 2 web framework
to implement. And also be limited by these 2 Python package's versions.

It could refer to the documentation about the Python version it supports of these 2 packages:

* Flask

> We recommend using the latest version of Python. Flask supports **Python 3.8 and newer**.We recommend using the latest version of Python. Flask supports Python 3.8 and newer.

[Here](https://flask.palletsprojects.com/en/2.3.x/installation/#python-version) is the reference about Python version it recommends.

* FastAPI

It's very short and clear:

> **Python 3.7+**

[Here](https://fastapi.tiangolo.com/lo/#requirements) is the reference about Python version it recommends.

That's the reason why **_PyMock-API_** supports Python 3.8 and newer. It needs to support both of these Python web frameworks.
