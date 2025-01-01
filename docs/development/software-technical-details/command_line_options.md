# Command line options

The logic which would parse the current command line and run something for it.

All codes belong to here section, they all are responsible for **defining the command line and its options to let _argpars_**
**understands how to parse the current command line.**

## UML

![software architecture - command line options]

[software architecture - command line options]: ../../_images/development/cmd_options_software_architecture.drawio.png

The software architecture here feature apply is mostly same as previous one section [Command line processors](#uml_1).

* It has 3 base classes:
    * ``MetaCommandOption``

        It's a metaclass for instantiating base class. It would auto-register objects which extends the base class be instantiated
        from this metaclass to list type data ``COMMAND_OPTIONS``. If it is sub-command, it also saves sub-command line string to
        list type data ``SUBCOMMAND``.

    * ``CommandOption`` (includes all subclasses of ``BaseSubCommand``)

        It defines all attributes and functions for subclass to reuse or override to implement customize logic.

    * ``BaseCmdOption``, ``BaseSubCmdRunOption``, etc.

        This is the base class which should be extended by all subclasses. This object be instantiated by metaclass ``MetaCommandOption``
        and general object ``CommandOption``.

* Every sub-command has their own base class. For example, sub-command line ``run`` with ``BaseSubCmdRunOption``, ``config``
with ``BaseSubCmdConfigOption`` and so on.
* The list be used by function ``get_all_subcommands`` is variable ``SUBCOMMAND``.
* The list be used by function ``make_options`` is variable ``COMMAND_OPTIONS``.
* All subclasses, i.e., ``Version`` extends ``BaseCmdOption``, ``WebAppType`` extends ``BaseSubCmdRunOption``, ``ConfigPath``
extends ``BaseSubCmdConfigOption``, etc., means the specific options under the sub-command line.

## Workflow

Because the software architecture of here section is mostly same with [Command line processors](#command-line-processors), its
workflow also could refer to its [workflow](#workflow_1).

## Extension

Here would demonstrate how to extend or add new sub-command feature.

You'll have 4 things:

* Add new attribute of data object **SubCommand**

Object ``SubCommand`` is the standard for **_PyMock-Server_** to recognize which sub-command it has. So let's add one new sub-command
line here:

```python hl_lines="9"
# In module pymock_server.command.options

@dataclass
class SubCommand:
    Base: str = "subcommand"
    Run: str = "run"
    Config: str = "config"
    Check: str = "check"
    NewProcess: str = "new-ps"
```

* Implement new class about subcommand ``new-ps``

Add new class extends base class ``BaseSubCommand`` and set value at attribute ``sub_parser``.

```python
# In module pymock_server.command.options

class SubCommandNewProcessOption(BaseSubCommand):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.NewProcess,
        help="New subcommand for demonstration,",
    )
```

* Instantiate class with metaclass for subcommand ``new-ps``

Instantiate a base class for adding options.

```python
# In module pymock_server.command.options

BaseSubCmdNewProcessOption: type = MetaCommandOption("BaseSubCmdNewProcessOption", (SubCommandNewProcessOption,), {})
```

It would auto-register this sub-command line into ``SUBCOMMAND``. We have sub-command line ``new-ps``, let's add its options.

* Extend the subcommand object to add its option(s)

Add new command option with extending ``BaseSubCmdNewProcessOption`` and set needed attributes in it:

```python
# In module pymock_server.command.options

class Arg_1(BaseSubCmdNewProcessOption):

    cli_option: str = "--arg-1"
    name: str = "arg_1"
    help_description: str = "A parameter for demonstration of extending new subcommand and new option."
```

* ``cli_option``: Define the option usage via command line.
* ``name``: The attribute to get the option value from _argpars_.
* ``help_description``: The description would be displayed if you run ``--help``.

Finally, don't forget to let command line process know which sub-command line is its responsibility by overriding the class
attribute ``responsible_subcommand``:

```python hl_lines="6"
# In module pymock_server.command.process

# ... some code

class SubCmdNewProcess(BaseCommandProcessor):
    responsible_subcommand = SubCommand.NewProcess

    # ... some code
```

Now, let's try to run the **_PyMock-Server_** with new sub-command:

```console
>>> mock new-ps --arg-1 test_value
This is new sub-command line and get option *arg_1*: test_value
```

Congratulation! It works finely as out expect.
