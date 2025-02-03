<h1 align="center">
  PyMock-Server
</h1>

<p align="center">
  <a href="https://pypi.org/project/fake-api-server">
    <img src="https://img.shields.io/pypi/v/fake-api-server?color=%23099cec&amp;label=PyPI&amp;logo=pypi&amp;logoColor=white" alt="PyPI package version">
  </a>
  <a href="https://github.com/Chisanan232/PyMock-Server/releases">
    <img src="https://img.shields.io/github/release/Chisanan232/PyMock-Server.svg?label=Release&logo=github" alt="GitHub release version">
  </a>
  <a href="https://github.com/Chisanan232/PyMock-Server/actions/workflows/ci.yaml">
    <img src="https://github.com/Chisanan232/PyMock-Server/actions/workflows/ci.yaml/badge.svg" alt="CI/CD status">
  </a>
  <a href="https://codecov.io/gh/Chisanan232/PyMock-Server">
    <img src="https://codecov.io/gh/Chisanan232/PyMock-Server/graph/badge.svg?token=r5HJxg9KhN" alt="Test coverage">
  </a>
  <a href="https://results.pre-commit.ci/latest/github/Chisanan232/PyMock-Server/master">
    <img src="https://results.pre-commit.ci/badge/github/Chisanan232/PyMock-Server/master.svg" alt="Pre-Commit building state">
  </a>
  <a href="https://sonarcloud.io/summary/new_code?id=Chisanan232_PyMock-Server">
    <img src="https://sonarcloud.io/api/project_badges/measure?project=Chisanan232_PyMock-Server&metric=alert_status" alt="Code quality level">
  </a>
  <a href="https://chisanan232.github.io/PyMock-Server/stable/">
    <img src="https://github.com/Chisanan232/PyMock-Server/actions/workflows/documentation.yaml/badge.svg" alt="documentation CI status">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="Software license">
  </a>

</p>

<img align="center" src="./_images/pymock-server_demonstration.gif" alt="pymock-server demonstration" />

<p align="center">
  <em>PyMock-Server</em> is a Python tool to mock API server easily and humanly without any coding.
</p>

## What things it wants to resolve?

Mock APIs through YAML file only, without any codes. And it also could easily and quickly set up a web server with the YAML format configuration.

## Why it is easy to use?

It provides command line tool to help developers could set up a web server quickly.

## Why it is humanly?

Its configuration has been designed for humanly understand what settings the API has.

## Requirements

Python 3.8+

**_PyMock-Server_** stands on the shoulder of giants:

* Frameworks and tools for web server and WSGI or ASGI server.
    * [**_Flask_**] with [**_Gunicorn_**]
    * [**_FastAPI_**] with [**_Uvicorn_**]

* [**_PyYAML_**] for processing YAML format data.

[**_Flask_**]: https://flask.palletsprojects.com/en/2.3.x/
[**_Gunicorn_**]: https://docs.gunicorn.org/
[**_FastAPI_**]: https://fastapi.tiangolo.com
[**_Uvicorn_**]: https://www.uvicorn.org/
[**_PyYAML_**]: https://pyyaml.org/wiki/PyYAMLDocumentation
