# PyFake-API-Server

[**_PyFake-API-Server_**](https://github.com/Chisanan232/PyFake-API-Server) is a tool for faking API server easily and quickly by configuration only.

[**_PyFake-API-Server**]: https://github.com/Chisanan232/PyFake-API-Server/tree/master

## How to use it?

You need to configure a YAML file to set API details. Let's demonstrate a sample configuration for you:

```yaml
mocked_apis:
  foo_home:
    url: '/foo'
    http:
      request:
        method: 'GET'
      response:
        strategy: string
        value: 'This is Foo home API.'
```

From above settings, it means setting an API:

* URL path: _/foo_
* Allow HTTP request method _GET_ without parameters
* If request successfully, it would return value ``This is Foo home API.``.

And save above setting as file ``/User/foo/fake-server-demo/api.yaml``.

Let's set up an instance to provide service:

```console
docker run --name fake-server \
           -v /User/foo/fake-server-demo:/mit-pyfake-api-server \
           -p 9672:9672 \
           -d \
           pyfake-api-server:v0.1.0
```

Try to send a HTTP request to the service:

```console
curl http://127.0.0.1:9672/foo
```

Congratulations! You successfully configure and set up a web server for faking API.

## Environment variables

When you set up a **_PyFake-API-Server_** instance by Docker, you can pass one or more environment variables to set its settings.

`CONFIG_PATH`

This is an option variable. It would set the file path where it should use to configure the APIs and set up web server.
In default, its value is ``api.yaml``.

`WEB_FRAMEWORK`

This is an option variable. The web framework **_PyFake-API-Server_** would use to set up web server to fake APIs. It only accepts
3 type values:

* ``auto``:

    This is the default value. It would automatically detect which web framework **_PyFake-API-Server_** could use in current
    runtime environment.

* ``flask``:

    Use Python web framework [**_Flask_**] to set up web server.

* ``fastapi``

    Use Python web framework [**_FastAPI_**] to set up web server.

[**_Flask_**]: https://flask.palletsprojects.com/en/2.3.x/
[**_FastAPI_**]: https://fastapi.tiangolo.com

`WORKERS`

This is an option variable. How many workers it should use to handle HTTP requests in the web server. In default, its value
is ``1``.

`LOG_LEVEL`

This is an option variable. Set the log level to let web server site show log message which is not below it. In default,
its value is ``info``.

## Quick reference

* More details of tutorial how to set configuration: [Getting started to configure your APIs].
* [More details] of configuring fake API.
* Find something works incorrectly? [Report a bug] to us.
* Have some great idea? Share with us and [request new feature or change].
* Want to know [entire knowledge of tool **_PyFake-API-Server_**].

[Getting started to configure your APIs]: https://chisanan232.github.io/PyFake-API-Server/stable/getting-started/configure-your-api/
[More details]: https://chisanan232.github.io/PyFake-API-Server/stable/configure-references/mocked-apis/
[Report a bug]: https://github.com/Chisanan232/PyFake-API-Server/issues/new?assignees=&labels=&projects=&template=reporting-a-bug.yaml
[request new feature or change]: https://github.com/Chisanan232/PyFake-API-Server/issues/new?assignees=&labels=&projects=&template=request-a-feature-or-change.yaml
[entire knowledge of tool **_PyFake-API-Server**]: https://chisanan232.github.io/PyFake-API-Server/stable/
