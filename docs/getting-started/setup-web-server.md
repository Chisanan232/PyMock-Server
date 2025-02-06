# Set up web server

If your configuration be ready to fake, it's time to set up a web server to fake them and provides this service to outside!

## Run by CLI

It's very easy to set up and run the web server by **_PyFake-API-Server_**. With default setting, namely using default value ``auto``
of option ``--app-type``, it would automatically detect which the Python web framework it can use in the current runtime
environment. Therefore, the running server log message would be different with different Python web framework.

=== "Flask"

    ``` sh
    >>> fake rest-server run -p <configuration path>
    [2023-06-06 21:55:53 +0800] [78900] [INFO] Starting gunicorn 20.1.0
    [2023-06-06 21:55:53 +0800] [78900] [INFO] Listening at: http://127.0.0.1:9672 (78900)
    [2023-06-06 21:55:53 +0800] [78900] [INFO] Using worker: sync
    [2023-06-06 21:55:53 +0800] [78915] [INFO] Booting worker with pid: 78915
    ```

=== "FastAPI"

    ``` sh
    >>> fake rest-server run -p <configuration path>
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

## Run by Docker

Although Docker is easy, but we should be careful to use it with options. It has three options are necessary you must use:

* ``-v``

    Mount the configuration of fake APIs into container. By Docker's rule, you need to use absolute path here. For the
    target path it would mount to, it must be in directory ``/mit-fake-api-server/`` because where is the command line works 
    at.

* ``-e``

    Set environment variable into container. It has some parameters it provides to use.

    * CONFIG_PATH

        The configuration path. By default, it would try to use file ``api.yaml`` in the root directory where it works at.
        In the other words, it would try to find the file ``/mit-fake-api-server/api.yaml`` in Docker container in default.
    
    * WEB_FRAMEWORK

        Which Python web framework it should use to set up server. By default, it would use ``auto`` to do it.
    
    * WORKERS

        How many workers it should use to process HTTP requests. By default, its value is ``1``.
    
    * LOG_LEVEL

        The log level of web server it should export. By default, its value is ``info``.

* ``-p``

    It needs to export the port number ``9672`` of web server so that it can provide the service to fake APIs for outside.

Let's give you a sample command line to set up fake server by **Docker**:

```console
>>> docker run --name fake-server \
               -v <configuration root directory>:/mit-fake-api-server/<configuration root directory> \
               -e CONFIG_PATH=<configuration path>
               -p 9672:9672 \
               fake-api-server:v0.1.0
```

??? tip "Hint: Still being confused about the configuration path setting? Let's demonstrate some usage scenarios to you."
    
    Assume that we have below files tree:
    
    ```console
    local root directory (/User/foo/fake-api-demo)
    ├── file1
    ├── file2
    ├── api.yaml
    ├── folder1
    │   ├── file3
    │   ├── file4
    │   └── beta-api.yaml
    ```

    * **Scenario 1: Use the configuration ``api.yaml``**

    Your command line would be like below:
    
    ```console
    >>> docker run --name fake-server \
                   -v /User/foo/fake-api-demo:/mit-fake-api-server \
                   -p 9672:9672 \
                   fake-api-server:v0.1.0
    ```
    
    You can mount the all files in folder ``/User/foo/fake-api-demo`` into folder
    ``/mit-fake-api-server`` of container. And the file tree in container would be as
    below:
    
    ```console
    container root directory (/)
    ├── mit-fake-api-server
    │   ├── file1
    │   ├── file2
    │   ├── api.yaml
    │   └── folder1
    |       ├── file3
    |       ├── file4
    │       └── beta-api.yaml
    ```
    
    Do you remember the command line working directory is ``mit-fake-api-server`` and
    the default value is ``api.yaml`` of environment ``CONFIG_PATH``? And it exactly
    has a file at path ``mit-fake-api-server/api.yaml`` so it would set up server successfully!

    * **Scenario 2: Use the configuration ``beta-api.yaml``**

    If you try to set up server by configuration ``beta-api.yaml``, your command
    line would be like below:
    
    ```console
    >>> docker run --name fake-server \
                   -v /User/foo/fake-api-demo:/mit-fake-api-server \
                   -e CONFIG_PATH=./folder1/beta-api.yaml
                   -p 9672:9672 \
                   fake-api-server:v0.1.0
    ```
    
    The mount setting is the same as previous scenario so the file tree also be the
    same as previous one. And the command line working directory is ``mit-fake-api-server``.
    So we just need to give it a relative path in working directory. Therefore, the
    value would be ``./folder1/beta-api.yaml``.

!!! note "What the detail usage of **_PyFake-API-Server_** by **Docker**?"

    Please refer to [PyFake-API-Server's image overview in Docker hub] to get more details.

    [PyFake-API-Server's image overview in Docker hub]: https://hub.docker.com/r/chisanan232/pyfake-api-server

Great! Now the web server for faking your API has done, and it would start to provide this service for other projects or
services.
