# Getting started

Actually, **_PyMock-Server_** is a Python package which provides command line tool. So it still needs to install a Python
package to activate the command line feature.


## Version requirements

**_PyMock-Server_** only supports _Python 3.8 and newer_ version.

**_PyMock-Server_** is a Python package which base on some giants to design and develop. It's obvious at the option ``--app-type``
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

That's the reason why **_PyMock-Server_** supports Python 3.8 and newer. It needs to support both of these Python web frameworks.


## Control version

Sometimes, it needs to run code with different Python versions. It strongly recommends using a tool **PyEnv** to manage
our Python version with current project.

### PyEnv <small>- Control and manage Python runtime environment</small>

It's a great tool of managing Python version for current runtime environment. It could be easily and quickly to switch current
Python runtime environment and manage multiple versions.

Please refer to the [documentation](https://github.com/pyenv/pyenv) of **PyEnv** to get more details. 

### Poetry <small>- Manage Python project's dependencies</small>

Why it also recommends using **Poetry**? It doesn't mean only use one of tools **PyEnv** or **Poetry**. It strongly recommends
to use both of them! Why? **PyEnv** could help you control and manage your current Python runtime environment, and **Poetry**
could strongly manage your project's dependencies. So you will be convenience and efficiency to develop and manage your Python
project.

[Here](https://python-poetry.org/docs/) is the documentation of **Poetry**. 
