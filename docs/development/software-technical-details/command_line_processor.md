# Command line processors

The logic which would run by the current command line you enter.

All codes belong to here section, they all are responsible for **what thing would happen after user run the command line**.

## UML

<iframe frameborder="0" style="width:100%;height:600px;" src="https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=PyMock-Server.drawio&page-id=p-yRdhPX9lBvFNy9WcaI#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1hq5q_Eaa8O48HgSEO8stAbWoS4HnwxEm%26export%3Ddownload"></iframe>

* It has 4 base classes:
    * ``MetaCommand``

        It's a metaclass for instantiating base class. It would auto-register objects which extends the base class be instantiated
        from this metaclass to list type protected variable ``_COMMAND_CHAIN``.

    * ``CommandProcessor``

        It defines all attributes and functions for subclass to reuse or override to implement customize logic.

    * ``BaseSubCmdComponent``

        This is the base class should be extended by all subclasses which is the core running logic implementation of one specific
        sub-command line. And it also needs to be the return value of property ``_subcmd_component`` of each subclass which extends
        base class ``CommandProcessor``.

    * ``BaseCommandProcessor``

        This is the base class which should be extended by all subclasses. This object be instantiated by metaclass ``MetaCommand``
        and general object ``CommandProcessor``.

* The list be used by function ``dispatch_command_processor`` is protected variable ``_COMMAND_CHAIN``.
* All subclasses, i.e., ``NoSubCmd``, ``SubCmdRun``, etc., extend ``BaseCommandProcessor`` and implement what thing they need
to do if user run the command includes returning which component they should use to run the core logic of the sub-command line.
* All subclasses, i.e., ``NoSubCmdComponent``, ``SubCmdRunComponent``, etc., extend ``BaseSubCmdComponent`` and implement the
truly core logic of the sub-command line with its options.

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

## Extension

Here would demonstrate how to add one new sub-command processor in this software architecture.

You'll have 3 things need to do:

* Command line argument

New sub-command line must have options. So you need to define which sub-command line options it has.

```python
# In module pymock_server.model.cmd_args

@dataclass(frozen=True)
class SubcmdNewProcessArguments(ParserArguments):
    arg_1: str
```

* Deserialization

After defining new sub-command line's options, you should define how to deserialize it:

```python
# In module pymock_server.model.cmd_args

class DeserializeParsedArgs:
  
    # ... some code

    @classmethod
    def subcommand_new_process(cls, args: Namespace) -> SubcmdNewProcessArguments:
        return SubcmdNewProcessArguments(
            subparser_name=args.subcommand,
            arg_1=args.arg_1,
        )
```

And also defining the utility function at module **_\_\_init\_\__**:

```python
# In module pymock_server.model.__init__

class deserialize_args:
  
    # ... some code

    @classmethod
    def subcmd_new_process(cls, args: Namespace) -> SubcmdNewProcessArguments:
        return DeserializeParsedArgs.subcommand_new_process(args)
```

* SubCommand process

Now, it has sub-command line option data object and deserialization, we could implement what thing it should do.

Here, we have 2 choices to implement: 

1. Override the function ``_run`` directly.
2. Add new class extends class ``BaseSubCmdComponent`` and implement property ``_subcmd_component``.

Let's demonstrate all way to implement to you and explain their difference.

  1. Override the function ``_run`` directly.
    
    In default, function ``_run`` would run the sub-command line core logic through the objects in component layer. In the other
    words, we also could override it directly without implement anything in component layer.
    
    * Pros:
    
        * Decrease the number of class for implementing or maintaining.
        * For the simple or easy logic, implement by this way could be more clear and short.
    
    * Cons:
    
        * For the complex logic or large-scale feature, implement by this way would let the code in this module to be dirty and
          complex so that developers be more harder to manage or maintain it.
    
    ```python
    # In module pymock_api.command.process
    
    # ... some code
    
    class SubCmdNewProcess(BaseCommandProcessor):
        def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdNewProcessArguments:
            return deserialize_args.subcmd_new_process(self._parse_cmd_arguments(parser, cmd_args))
    
        def _run(self, args: SubcmdNewProcessArguments) -> None:
            # Do something ...
            print(f"This is new sub-command line and get option *arg_1*: {args.arg_1}.")
    ```

  2. Add new class extends class ``BaseSubCmdComponent`` and implement property ``_subcmd_component``.
    
    Implement and manage the core logic in component layer. And the **_command.process_** module only needs to know which component
    object is responsible of this feature.
    
    * Pros:
    
        * Decoupling the logics sub-command line processor and core logic of the sub-command line.
        * Could be more higher cohesion of the core logic of sub-command line with its options.
        * No matter how the sub-command logic complex is, it still could be more easier and maitainable for management.
    
    * Cons:
    
        * More classes, more management.
        * If the core logic is very easy and short, this way is a little laborious.
    
    Implement the core logic in component layer:

    ```python
    # In module pymock_api.command.new_subcmd.component
      
    # ... some code
    
    class SubCmdNewProcessComponent(BaseSubCmdComponent):
        def process(self, args: SubcmdNewProcessArguments) -> None:
            # Do something ...
            print(f"This is new sub-command line and get option *arg_1*: {args.arg_1}.")
    ```
    
    Remember that it needs to let command line processor know which component object it should use to run the sub-command line core logic:

    ```python
    # In module pymock_api.command.process
    
    # ... some code
    
    class SubCmdNewProcess(BaseCommandProcessor):
        @property
        def _subcmd_component(self) -> SubCmdRunComponent:
            return SubCmdNewProcessComponent()
    
        def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdNewProcessArguments:
            return deserialize_args.subcmd_new_process(self._parse_cmd_arguments(parser, cmd_args))
    ```

We finish all things if we want to extend one new sub-command line! Let's try to run it:

```console
>>> mock new-ps --arg-1 test_value
```

Unfortunately, you would get an error finally. Why? What you miss? Do you remember all the code in this software architecture
only process the logic it should run by the current command line? But, how does it parse the command line and its options? So
next section would tell you how to add new sub-command line and its options in their software architecture.
