# ``rest-server run`` - web server

This is the core feature of **_PyMock-Server_**. It does 2 things:

* Set up web application with the API from the detail settings of configuration.
* Run the web application by SGI server.

## UML

![software architecture - web server with sgi server]

[software architecture - web server with sgi server]: ../../_images/development/server_software_architecture.drawio.png

* The sub-command line processor ``SubCmdRun`` would use function ``setup_wsgi`` or ``setup_asgi`` to run the web application.
* All the way to run web application by factory pattern in **_PyMock-Server_**.
* The functions as factory callee to set up web application is ``create_flask_app`` and ``create_fastapi_app``.
* Functions ``create_flask_app`` or ``create_fastapi_app`` would use adapter ``MockHTTPServer`` to set up all APIs as Python
code with Python web framework **_Flask_** or **_FastAPI_**.

## Extension

If you have your own customize Python web framework, you also could extend this features by your own one.

Here would demonstrate how to extend it to implement your own web server.

First, the entire web server should be divided to 2 parts:

* Server implementation from Python web framework
* Server gateway interface (a.k.a SGI) server

They mean you should extend all below classes to implement:

* For setting up web application by generating Python code
    * ``BaseAppServer``

* For running web application by SGI server
    * ``BaseSGIServer``
    * ``BaseCommandOption``

Don't forget it also needs to import the Python web framework into **_PyMock-Server_** to let it could generate Python code about
APIs with configuration.

* Import web library

2 Things you need to implement: importing the web framework and check importing the web framework.

```python
# In module pymock_server._utils.importing

class import_web_lib:

    # Some code ...

    @staticmethod
    def foo_web_lib() -> "foo_web_lib":
        import foo_web_lib

        return foo_web_lib

    # Some code ...

    @staticmethod
    def foo_web_lib_ready() -> bool:
        return import_web_lib._chk_lib_ready(import_web_lib.foo_web_lib)
```

!!! note "Importing way may be different with different web framework"

    The importing way should be based on how to use the customized Python web framework.

* ``BaseAppServer``

Extend the web application feature about how PyMock-Server should set up it? How to initial the web application by the customized
Python web framework? How to add new API by the customized web framework?

```python
# In module pymock_server.server.application

class FooWebLibrary(BaseAppServer):
    def setup(self) -> "foo_web_lib.Foo":
        # How to set up web application instance by this web library
        return import_web_lib.foo_web_lib().Foo(__name__)

    def _add_api(self, api_name: str, api_config: MockAPI, base_url: Optional[str] = None) -> str:
        # How to add API by this web library
        return f"""self.web_application.add_web_route(
            path="{self.url_path(api_config, base_url)}", methods=["{cast(HTTPRequest, self._ensure_http(api_config, "request")).method}"]
            )({api_name})
        """
```

* ``BaseSGIServer``

Implement how to run web application by your own customized Python web framework. In exactly, it just generates a command line
with options.

```python
# In module pymock_server.server.sgi.cmd

class FooSGIServer(BaseSGIServer):
    def _init_cmd_option(self) -> BaseCommandOption:
        return FooWebSGIServerCmdOption()

    @property
    def entry_point(self) -> str:
        return "foonicorn"
```

* ``BaseCommandOption``

Previous one implement the command line entry point, here implement each options how to set it.

```python
# In module pymock_server.server.sgi.cmdoption

class FooWebSGIServerCmdOption(BaseCommandOption):
    def bind(self, address: Optional[str] = None, host: Optional[str] = None, port: Optional[str] = None) -> str:
        # Set the option about binding the service at one or more specific hosts
        if address:
            self._is_valid_address(address)
            binding_addr = address
        elif host and port:
            binding_addr = f"{host}:{port}"
        else:
            raise ValueError("There are 2 ways to pass arguments: using *address* or using *host* and *port*.")
        return f"--bind {binding_addr}"

    def workers(self, w: int) -> str:
        # Set the option about how many workers could handle the requests
        return f"--workers {w}"

    def log_level(self, level: str) -> str:
        # Set the option about log level
        return f"--log-level {level}"
```

Now, we have done the core implementation, then we just leave some utility functions which we need to add.

* Utility function in module ``pymock_api.server.sgi.__init__``

```python hl_lines="10"
# In module pymock_server.server.sgi.__init__

class setup_server_gateway:
    # Some code ...

    @classmethod
    def foo(cls, web_app: Union[str, Callable], module_dict: Optional[dict] = None) -> FooSGIServer:
        if module_dict:
            cls._ensure_function_exists(web_app, module_dict)
        return FooSGIServer(app=f"{web_app.__qualname__}()" if isinstance(web_app, Callable) else web_app)

# Some code ...
```

Please take a look at the code line 10, it's the key line to let SGI server to catch which factory function it should use to
generate the web application. Here usage should base on which way should use by your own customized Python web framework.

* Utility function in module ``pymock_api.server.__init__``

```python
# In module pymock_server.server.__init__

# Some code ...

foo_app: "foo_web_lib.Foo" = None

# Some code ...

def create_foo_app() -> "foo_web_lib.Foo":
    load_app.by_foo()
    return foo_app

# Some code ...

def setup_foosgi() -> FooSGIServer:
    return setup_server_gateway.foo(web_app=create_foo_app, module_dict=globals())

# Some code ...

class load_app:

    @classmethod
    @ensure_importing(import_web_lib.foo_web_lib)
    def by_foo(cls) -> None:
        global foo_app
        config = cls._get_config_path()
        foo_app = cls._initial_mock_server(config_path=config, app_server=FooWebLibrary()).web_app

# Some code ...
```

The global variable ``foo_app`` is the variable which web application instance will be saved at. Function ``create_foo_app`` is
the factory function to generate web application. Function ``setup_foosgi`` is the one which runs the web application which be
set up by your own customized Python web framework.

* Add option value in one specific function in module ``pymock_api.command.process``

Finally, we need to add a new value to let option ``--app-type`` could recognize and dispatch it to set up and run the web
application by your own customized Python web framework.

```python hl_lines="19-20"
# In module pymock_server.command.process

# Some code ...

class SubCmdRun(BaseCommandProcessor):
    
    # Some code ...

    def _initial_server_gateway(self, lib: str) -> None:
        if re.search(r"auto", lib, re.IGNORECASE):
            web_lib = import_web_lib.auto_ready()
            if not web_lib:
                raise NoValidWebLibrary
            self._initial_server_gateway(lib=web_lib)
        elif re.search(r"flask", lib, re.IGNORECASE):
            self._server_gateway = setup_wsgi()
        elif re.search(r"fastapi", lib, re.IGNORECASE):
            self._server_gateway = setup_asgi()
        elif re.search(r"foo", lib, re.IGNORECASE):
            self._server_gateway = setup_foosgi()
        else:
            raise InvalidAppType

# Some code ...
```

All things you need to do is done! Let's try to run the command line to test its feature:

```console
>>> mock --app-type foo
```

If you could keep observing the log message which be generated by web application as you expect, congratulation you extend the
feature successfully!
