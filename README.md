# PyMock-Server

[![PyPI](https://img.shields.io/pypi/v/PyMock-Server?color=%23099cec&amp;label=PyPI&amp;logo=pypi&amp;logoColor=white)](https://pypi.org/project/PyMock-Server)
[![Release](https://img.shields.io/github/release/Chisanan232/PyMock-Server.svg?label=Release&logo=github)](https://github.com/Chisanan232/PyMock-Server/releases)
[![CI](https://github.com/Chisanan232/PyMock-Server/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Chisanan232/PyMock-Server/actions/workflows/ci-cd.yml)
[![codecov](https://codecov.io/gh/Chisanan232/PyMock-Server/graph/badge.svg?token=r5HJxg9KhN)](https://codecov.io/gh/Chisanan232/PyMock-Server)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Chisanan232/PyMock-Server/master.svg)](https://results.pre-commit.ci/latest/github/Chisanan232/PyMock-Server/master)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Chisanan232_PyMock-Server&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Chisanan232_PyMock-Server)
[![documentation](https://github.com/Chisanan232/PyMock-Server/actions/workflows/documentation.yaml/badge.svg)](https://chisanan232.github.io/PyMock-Server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python tool to mock API easily and humanly without any coding.

> [!NOTE]
> It names **_PyMock-API_** before version **0.2.0**.
>
> [![PyPI](https://img.shields.io/pypi/v/PyMock-API?color=%23099cec&amp;label=PyPI&amp;logo=pypi&amp;logoColor=white)](https://pypi.org/project/PyMock-API)

[Overview](#overview) | [Python versions support](#Python-versions-support) | [Quickly Start](#quickly-start) | [Documentation](#documentation)
<hr>


## Overview

Do you ever have experience about needing to set up a very simple application and write some APIs with hardcode response again and again
for developing Font-End site? **_PyMock-Server_** provides a command line tool to let developers could quickly and easily set up application
to mock APIs with configuration only.


## Python versions support

The code base of **_PyMock-Server_** to set up an application still depends on third party Python package, i.e., **_Flask_**, **_FastAPI_**,
etc. So the Python versions it supports also be affected by them, e.g., **_Flask_** only supports Python version 3.8 up currently. So
**_PyMock-Server_** also only supports version Python 3.8 up.

[![Supported Versions](https://img.shields.io/pypi/pyversions/PyMock-Server.svg?logo=python&logoColor=FBE072)](https://pypi.org/project/PyMock-Server)


## Quickly Start

Here section would lead you quickly start to set up your first one application by **_PyMock-Server_** for mocking APIs easily.

In basically, it has 3 steps: install the package, configure settings about the APIs for mocking and run command.

* [Install](#install-command-line-tool)
* [Configure](#configure-setting-to-mock-target-apis)
* [Run](#run-command-to-set-up-application)

### Install command line tool

First of all, we need to install the command line tool and the way to install is same as installing Python package by ``pip``.

```console
>>> pip install pymock-server
```

If the runtime environment has installed some Python web framework, e.g., **_Flask_**, you also could install **_Pymock-Server_**
with one specific option as following:

```console
>>> pip install "pymock-server[flask]"
```

Then it would only install the lowest Python dependencies you need.

After you done above step, please make sure the command line tool feature should work finely by below command:

```console
>>> mock --help
```

> **Note**
>
> Please take a look at option _--app-type_ (this option is in subcommand **_mock run_**) of the command line tool. Its option
> value could be ``auto``, ``flask`` or ``fastapi``. It means that **_PyMock-Server_** only supports 2 Python web frameworks: **_Flask_**
> and **_FastAPI_**.

### Configure setting to mock target APIs

Now, we have the command line tool. Let's configure the settings it needs to set up application to mock API.

The configuration format of **_PyMock-Server_** to use is **YAML**. So let's write below settings in YAML file:

```yaml
mocked_apis:
  google_home:
    url: '/google'
    http:
      request:
        method: 'GET'
      response:
        strategy: string
        value: 'This is Google home API.'
```

### Run command to set up application

Now, both of the command line tool and configuration have been already. So let's try to run the command to set up application!

```console
>>> mock rest-server run -c <your configuration path>
```

You would see some log messages in terminal and that is the log of web server by one specific Python web framework.

And you could test the API by ``curl``:

```console
>>> curl http://127.0.0.1:9672/google
"This is Google home API."%
```

![demonstration](./docs/images/demonstration_pymock-api_cli.gif)

## Documentation

Currently, it won't have documentation. But it would have soon.


## Coding style and following rules

**_PyMock-Server_** follows coding styles **_black_** and **_PyLint_** to control code quality.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)


## Downloading state

**_PyMock-Server_** still a young open source which keep growing. Here's its download state:

[![Downloads](https://pepy.tech/badge/PyMock-Server)](https://pepy.tech/project/PyMock-Server)
[![Downloads](https://pepy.tech/badge/PyMock-Server/month)](https://pepy.tech/project/PyMock-Server)


## License

[MIT License](./LICENSE)
