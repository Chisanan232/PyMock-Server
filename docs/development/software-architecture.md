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

```python
from pymock_api.cmd import BaseSubCommand

class SubCommandNewProcessOption(BaseSubCommand):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.Config,
        help="Something processing about configuration, i.e., generate a sample configuration or validate configuration"
        " content.",
    )
```

content ...

```python
from pymock_api.cmd import MetaCommandOption

BaseSubCmdNewProcessOption: type = MetaCommandOption("BaseSubCmdNewProcessOption", (SubCommandRunOption,), {})
```

content ...

```python
class SubCmdNewProcess(BaseCommandProcessor):
    def read(self):
        return 
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

* BaseAppServer

content ...

```python
from pymock_api.server.application import BaseAppServer

class FooWebLibrary(BaseAppServer):
    def read(self):
        return 
```

* BaseSGIServer

content ...

```python
from pymock_api.server.sgi.cmd import BaseSGIServer

class FooSGIServerCmd(BaseSGIServer):
    def read(self):
        return 
```

* BaseCommandOption

content ...

```python
from pymock_api.server.sgi.cmdoption import BaseCommandOption

class FooWebSGIServerCmdOption(BaseCommandOption):
    def read(self):
        return 
```

content ...
