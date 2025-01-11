# Command line

The logic is a little bit complex and also is a big software architecture at command line option part.

Before how to extend the new command line and implement its feature, this section records the details of the command
line part design and implementation.

## Implementation details

About a whole command line structure, we can divide it as multiple parts to describe its details:

* Pure value
    * Enum object about command line section **_SubCommandSection_**
    * Enum object about command line **_SubCommandLine_**
* Object for truly function
    * Base data model about major command line **_BaseSubCommandXXX_**
    * Base data model about subcommand line **_SubCommandXXXOption_** for its options
    * Command line options of the subcommand line **_SubCommandXXXOption_**

!!! note "What is different between **Pure value** and **Object for truly function**?"

    * **Pure value**

        It just the value you can use for the command line feature to display, use
        look like. But it DOES NOT have truly function to work.

    * **Object for truly function**

        This sections are the implementations which could setup a truly features for
        working finely. In generally, these sections would use the value from previous
        one **Pure value**.

### Pure value

#### Command line section value in **_SubCommandSection_**

[source code](https://github.com/Chisanan232/PyMock-Server/blob/master/pymock_server/command/subcommand.py#L33-L35)

This is the section title of subcommand line usage. Each new subcommand line should define this value for brief of
subcommand line operations.

```python
# code usage of a command line option

class SubCommandSection(Enum):
    Base = "subcommands"
    ApiServer = "API server subcommands"
    Foo = "Foo command line"
```

![command line section]

[command line section]: ../../_images/development/contributing/software_technical_details/cli_section_mock_help.png

#### Command line value in **_SubCommandLine_**

[source code](https://github.com/Chisanan232/PyMock-Server/blob/master/pymock_server/command/subcommand.py#L7-L30)

This is the command line self string value what it is.

```python
# code usage of a command line option

class SubCommandLine(Enum):
    Base = "subcommand"

    # some code here ...

    Foo = "foo"
    Boo = "boo"
```

![command line]

[command line]: ../../_images/development/contributing/software_technical_details/cli_line_mock_help.png

### Object for truly function

#### Major command line **_BaseSubCommandXXX_**

[example source code](https://github.com/Chisanan232/PyMock-Server/blob/master/pymock_server/command/options.py#L77-L86)

This is the top implementation layer of command line data models. **_PyMock-Server_** command line tool is a nested
command line structure. And this layer is the top layer means the first layer command line.

```python
# code usage of a command line option

class BaseMajorCommandFoo(CommandOption):
    sub_cmd: SubCommandAttr = SubCommandAttr(
        title=SubCommandSection.Foo,
        dest=SubCommandLine.Foo,
        description="Some operations for foo.",
        help="Demonstrate for foo.",
    )
    in_sub_cmd = SubCommandLine.Foo
```

![major command line]

[major command line]: ../../_images/development/contributing/software_technical_details/cli_line_mock_help.png

#### Subcommand command line **_SubCommandXXXOption_**

[example source code](https://github.com/Chisanan232/PyMock-Server/blob/master/pymock_server/command/rest_server/run/options.py#L9-L17)

Previous one is the top layer, this layer is the layers which are under second layer.

!!! note "Subcommand line must identify one specific major command line"

    This layer command line data model would extend one specific major command line
    data model, which means it would only runs under one specific command line. So
    please take care what command line it should use to extend its features.

    Below demonstration is extend feature under the parent command line ``foo``.

```python
# code usage of a command line option

class SubCommandBooOption(BaseMajorCommandFoo):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommandLine.Boo,
        help="Set up a boo CLI for foo.",
    )
    option_value_type: type = str


BaseSubCmdBooOption: type = MetaCommandOption("BaseSubCmdBooOption", (SubCommandBooOption,), {})
```

![subcommand lines]

[subcommand lines]: ../../_images/development/contributing/software_technical_details/cli_line_mock_rest-server_help.png

#### Options of subcommand command line **_SubCommandXXXOption_**

[example source code](https://github.com/Chisanan232/PyMock-Server/blob/master/pymock_server/command/rest_server/run/options.py#L20-L63)

This is the truly command line options. Any command line option properties, i.e., option name, help description of
option, etc., would be set here.

[//]: # (TODO: Support API reference like below)
[//]: # (::: pymock_server.command._base.options.CommandOption)

```python
# code usage of a command line option

class CmdOption(BaseSubCmdBooOption):
    cli_option: str = "-o, --option"
    name: str = "option"
    help_description: str = "The sample command line option setting."
    default_value: str = "test value"
```

![subcommand line option]

[subcommand line option]: ../../_images/development/contributing/software_technical_details/cli_option_mock_rest-server_run_help.png

## UML

<iframe frameborder="0" style="width:100%;height:800px;" src="https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=PyMock-Server.drawio&page-id=b7Q_UegN4KtkyAv_nRkj#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1hq5q_Eaa8O48HgSEO8stAbWoS4HnwxEm%26export%3Ddownload"></iframe>

* It has 3 base classes:
    * ``MetaCommandOption`` [source code](https://github.com/Chisanan232/PyMock-Server/blob/master/pymock_server/command/_base/options.py#L53-L81)

        It's a metaclass for instantiating base class. It would auto-register objects which extends the base class be instantiated
        from this metaclass to list type data ``COMMAND_OPTIONS``. If it is sub-command, it also saves sub-command line string to
        list type data ``SUBCOMMAND``.

    * ``CommandOption`` (includes all subclasses of ``BaseSubCommand``) [source code](https://github.com/Chisanan232/PyMock-Server/blob/master/pymock_server/command/_base/options.py#L87-L240)

        It defines all attributes and functions for subclass to reuse or override to implement customize logic.

    * [``BaseCmdOption``](https://github.com/Chisanan232/PyMock-Server/blob/master/pymock_server/command/options.py#L77-L86), [``BaseSubCommandRestServer``](https://github.com/Chisanan232/PyMock-Server/blob/master/pymock_server/command/rest_server/option.py#L6-L13), etc.

        This is the base class which should be extended by all subclasses. This object be instantiated by metaclass ``MetaCommandOption``
        and general object ``CommandOption``.

* Every sub-command has their own base class. For example, sub-command line ``run`` with ``BaseSubCmdRunOption``, ``config``
with ``BaseSubCmdConfigOption`` and so on.
* The list be used by function ``get_all_subcommands`` is variable ``SUBCOMMAND``.
* The list be used by function ``make_options`` is variable ``COMMAND_OPTIONS``.
* All subclasses, i.e., ``Version`` extends ``BaseCmdOption``, ``WebAppType`` extends ``BaseSubCmdRunOption``, ``ConfigPath``
extends ``BaseSubCmdConfigOption``, etc., means the specific options under the sub-command line.

??? note "The great idea about **auto-register** refer to source code of project **_Gunicorn_**"

    About the powerful design **auto-register** which has beautiful extension, it
    refers to the module _config_ implementation of open source project **_Gunicorn_**.
    Please refer to [its source code] if you have interesting in it.

    [its source code]: https://github.com/benoitc/gunicorn/blob/master/gunicorn/config.py

## Workflow

* Sequence diagram

<iframe frameborder="0" style="width:100%;height:400px;" src="https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=PyMock-Server.drawio&page-id=y4nP58FJjcgKiph7c4k3#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1hq5q_Eaa8O48HgSEO8stAbWoS4HnwxEm%26export%3Ddownload"></iframe>

From above sequence diagram, it does auto-registration when initialize an object. It won't do something to iterate all objects
and save them to list type object, it automates all things when you add one or more new subclasses which is responsible for new
sub-command line.
