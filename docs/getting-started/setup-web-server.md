# Set up web server

If your configuration be ready to mock, it's time to set up a web server to mock them and provides this service to outside!

## Run by CLI

It's very easy to set up and run the web server by **_PyMock-API_**. With default setting, namely using default value ``auto``
of option ``--app-type``, it would automatically detect which the Python web framework it can use in the current runtime
environment. Therefore, the running server log message would be different with different Python web framework.

=== "Flask"

    ``` sh
    >>> mock-api run -p <configuration path>
    [2023-06-06 21:55:53 +0800] [78900] [INFO] Starting gunicorn 20.1.0
    [2023-06-06 21:55:53 +0800] [78900] [INFO] Listening at: http://127.0.0.1:9672 (78900)
    [2023-06-06 21:55:53 +0800] [78900] [INFO] Using worker: sync
    [2023-06-06 21:55:53 +0800] [78915] [INFO] Booting worker with pid: 78915
    ```

=== "FastAPI"

    ``` sh
    >>> mock-api run -p <configuration path>
    INFO:     Started server process [78594]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://127.0.0.1:9672 (Press CTRL+C to quit)
    ```

After running the web server, let's try to send HTTP request by command line ``curl`` to the API and verify its feature.

```shell
>>> curl -X GET http://127.0.0.1:9672/foo
"This is Foo home API."%
```

Great! Now the web server for mocking your API has done, and it would start to provide this service for other projects or
services.
