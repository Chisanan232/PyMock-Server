# Software architecture

content ...


## Program entry point - command line runner

content ...

### UML

![software architecture - command runner]

[software architecture - command runner]: ../../images/development/cmd_runner_software_architecture.drawio.png

content ...

### Workflow

content ...


## Command line features

content ...

### Option ``--config`` - file operation

content ...

#### UML

![software architecture - operation with file]

[software architecture - operation with file]: ../../images/development/file_operatrions_software_architecture.drawio.png

content ...

#### Workflow

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

#### Extension

content ...

* SubCommand process

content ...

```python
from pymock_api.cmd_ps import BaseCommandProcessor

class SubCmdNewProcess(BaseCommandProcessor):
    def read(self):
        return 
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
