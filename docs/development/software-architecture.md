# Software architecture

Software architecture is very important in a production because it's relative the flexibility and extensibility of the production.
So it must have design 


## Program entry point - command line runner

content ...

### UML

![software architecture - command runner]

[software architecture - command runner]: ../../images/development/cmd_runner_software_architecture.drawio.png

content ...

### Workflow

content ...

![sequence diagram - command runner]

[sequence diagram - command runner]: ../../images/development/cmd_runner_sequence_diagram.drawio.png

content ...


## Command line features

content ...

### Option ``--config`` - file operation

content ...

#### UML

![software architecture - operation with file]

[software architecture - operation with file]: ../../images/development/file_operatrions_software_architecture.drawio.png

content ...

#### Extension

content ...

* File operation

content ...

```python
from pymock_api._utils.file_opt import _BaseFileOperation

class JSON(_BaseFileOperation):
    def read(self):
        return 
```

content ...


### Command line processors

content ...

#### UML

![software architecture - command line processor]

[software architecture - command line processor]: ../../images/development/cmd_ps_software_architecture.drawio.png

content ...

#### Workflow

content ...

![sequence diagram - auto register by meta class]

[sequence diagram - auto register by meta class]: ../../images/development/meta-class_auto-register_sequence_diagram.drawio.png

#### Extension

content ...

* Command line argument

content ...

```python
# In module pymock_api.model.cmd_args

@dataclass(frozen=True)
class SubcmdNewProcessArguments(ParserArguments):
    arg_1: str
```

content ...

* Deserialization

content ...

```python
class DeserializeParsedArgs:
  
    # ... some code

    @classmethod
    def subcommand_new_process(cls, args: Namespace) -> SubcmdNewProcessArguments:
        return SubcmdNewProcessArguments(
            subparser_name=args.subcommand,
            arg_1=args.arg_1,
        )
```

content ...

```python
class deserialize_args:
    @classmethod
    def subcmd_new_process(cls, args: Namespace) -> SubcmdNewProcessArguments:
        return DeserializeParsedArgs.subcommand_new_process(args)
```

content ...

* SubCommand process

content ...

```python
from argparse import ArgumentParser
from typing import List, Optional
from pymock_api.cmd_ps import BaseCommandProcessor

class SubCmdNewProcess(BaseCommandProcessor):
    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdNewProcessArguments:
        return deserialize_args.subcmd_new_process(self._parse_cmd_arguments(parser, cmd_args))

    def _run(self, args: SubcmdNewProcessArguments) -> None:
        # Do something ...
        pass
```

content ...


### Command line options

content ...

#### UML

![software architecture - command line options]

[software architecture - command line options]: ../../images/development/cmd_options_software_architecture.drawio.png

content ...

#### Workflow

content ...

[workflow](#workflow_1)

content ...

#### Extension

content ...

* SubCommand process
    * Sub-command class
    * Class which be instantiated from meta class with sub-command class
    * The options as classes which extends from the instance

content ...

* Add new attribute of data object **SubCommand**

content ...

```python hl_lines="7"
@dataclass
class SubCommand:
    Base: str = "subcommand"
    Run: str = "run"
    Config: str = "config"
    Check: str = "check"
    NewProcess: str = "new-ps"
```

content ...

* Implement new class about subcommand ``new-ps``

content ...

```python
from pymock_api.cmd import BaseSubCommand

class SubCommandNewProcessOption(BaseSubCommand):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.NewProcess,
        help="New subcommand for demonstration,",
    )
```

content ...

* Instantiate class with metaclass for subcommand ``new-ps``

content ...

```python
from pymock_api.cmd import MetaCommandOption

BaseSubCmdNewProcessOption: type = MetaCommandOption("BaseSubCmdNewProcessOption", (SubCommandNewProcessOption,), {})
```

content ...

* Extend the subcommand object to add its option(s)

content ...

```python
class Arg_1(BaseSubCmdNewProcessOption):

    cli_option: str = "--arg-1"
    name: str = "arg_1"
    help_description: str = "A parameter for demonstration of extending new subcommand and new option."
```

content ...


## SubCommand features

content ...


### ``run`` - web server

content ...

#### UML

![software architecture - web server with sgi server]

[software architecture - web server with sgi server]: ../../images/development/server_software_architecture.drawio.png

content ...

#### Workflow

content ...

#### Extension

content ...

* Web server
    * Server implementation from Python web framework
    * Server gateway interface (a.k.a SGI) server

content ...

* BaseAppServer
* BaseSGIServer
* BaseCommandOption

content ...

* Import web library

content ...

```python
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

content ...

* BaseAppServer

content ...

```python
from pymock_api.server.application import BaseAppServer

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

* BaseSGIServer

content ...

```python
from pymock_api.server.sgi.cmd import BaseSGIServer

class FooSGIServerCmd(BaseSGIServer):
    def _init_cmd_option(self) -> BaseCommandOption:
        return FooWebSGIServerCmdOption()

    @property
    def entry_point(self) -> str:
        return "foonicorn"
```

* BaseCommandOption

content ...

```python
from pymock_api.server.sgi.cmdoption import BaseCommandOption

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

content ...
