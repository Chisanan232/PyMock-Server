# Subcommand ``run`` usage

Activate and run a web server which could provide all the APIs be configured in ``.yaml`` configuration file. The way for
running the web server would be different if the web library is different so that the log message would be different.

```console
>>> mock rest-server run <option>
```


## ``--config`` or ``-c`` <config-file-path\>

Set the configuration file path. **_PyFake-API-Server_** would use the settings to configure the APIs.

It receives a value about the configuration file path and its default value is ``api.yaml``.


## ``--app-type`` <Python-web-library\>

Set one of Python web framework which would be the code base of the web server for mocking APIs.

It receives a value about the Python web framework. The options it accepts are ``auto``, ``flask`` and ``fastapi``.

* ``auto``
    
    It would automatically detect which Python web framework it could use in current runtime environment. If it doesn't have
    any web framework could use, it would exit the program finally.

* ``flask``
    
    Use Python web framework [**_Flask_**] to be the code base of the web server for mocking APIs.

[**_Flask_**]: https://flask.palletsprojects.com/en/2.3.x/

* ``fastapi``
    
    Use Python web framework [**_FastAPI_**] to be the code base of the web server for mocking APIs.

[**_FastAPI_**]: https://fastapi.tiangolo.com

Its default value is ``auto``.


## ``--bind`` or ``-b`` <host-address\>

Set the host to bind with the web server.

It receives a value about the host address which should includes IP address and port. Its default value is ``0.0.0.0:9672``.

!!! question "Why the default port is **9672**?"

    The port number could be divides into 2 parts: **96** and **72**. These 2 number mean an important thing in history:
    In **1996**, the NBA G.O.A.T Michael Jordan leaded the Chicago Bulls team won **72** games and won the NBA champion
    in that season finally. He has keeped making history and has so many unbelievable records in NBA history. Therefore,
    **_PyFake-API-Server_** uses the port number **9672** to remember the things this legend made.


## ``--workers`` or ``-w`` <workers\>

Set the amount how many workers does it process the requests of web server.

It receives a value about the amount of workers and its default value is ``1``.


## ``--log-level`` <level\>

Set the log level of web server what info it should export.

It receives a value about the log level and its default value is ``info``.
