# Command line options

The logic which would parse the current command line and run something for it.

All codes belong to here section, they all are responsible for **defining the command line and its options to let _argpars_**
**understands how to parse the current command line.**

## UML

About the software architecture of this feature is already be introduced. Please refer to section [Command line - UML](command_line.mdml).

## Workflow

About the software workflow details of this feature is already be introduced. Please refer to section [Command line - Workflow](command_line.mdorkflow).

## Extension

Here would demonstrate how to extend or add new sub-command feature.

You'll have 4 things:

### Add new attribute of enum object **SubCommandLine**

Enum object ``SubCommandLine`` is the standard for **_PyFake-API-Server_** to recognize which sub-command it has. So let's add 
one new sub-command line here:

```python hl_lines="9"
# In module fake_api_server.command.subcommand

class SubCommandLine(Enum):

    # other enum ...

    NewProcess: str = "new-ps"
```

### Implement new class about subcommand ``new-ps``

Add new class extends base class ``BaseSubCommand`` and set value at attribute ``sub_parser``.

```python
# In module fake_api_server.command.new_subcmd.options

class SubCommandNewProcessOption(BaseSubCommand):
    sub_cmd: SubCommandAttr = SubCommandAttr(
        title=SubCommandSection.Base,
        dest=SubCommandLine.Base,
        description="",
        help="",
    )
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.NewProcess,
        help="New subcommand for demonstration,",
    )
```

### Instantiate class with metaclass for subcommand ``new-ps``

Instantiate a base class for adding options.

```python
# In module fake_api_server.command.options

BaseSubCmdNewProcessOption: type = MetaCommandOption("BaseSubCmdNewProcessOption", (SubCommandNewProcessOption,), {})
```

It would auto-register this sub-command line into ``SUBCOMMAND``. We have sub-command line ``new-ps``, let's add its options.

### Extend the subcommand object to add its option(s)

Add new command option with extending ``BaseSubCmdNewProcessOption`` and set needed attributes in it:

```python
# In module fake_api_server.command.options

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
# In module fake_api_server.command.process

# ... some code

class SubCmdNewProcess(BaseCommandProcessor):
    responsible_subcommand = SubCommand.NewProcess

    # ... some code
```

Now, let's try to run the **_PyFake-API-Server_** with new sub-command:

```console
>>> mock new-ps --arg-1 test_value
This is new sub-command line and get option *arg_1*: test_value
```

Congratulation! It works finely as out expect.
