# Program entry point - command line runner

The entry point of **_PyMock-Server_** command line tool. Its actually entry point is calling the function ``run`` in module
``pymock_api.runner``.

## UML

![software architecture - command runner]

[software architecture - command runner]: ../../images/development/cmd_runner_software_architecture.drawio.png

* About the function which would be run as entry point ``run``, it's a running logic of object ``CommandRunner``.
* Object ``CommandRunner`` would keep instance of ``ArgumentParser`` and ``CommandProcessor`` to parse command line and run
core logic of the current sub-command.
* Object ``CommandRunner`` would use function ``dispatch_command_processor`` to get the correct instance to handle current
command line.

## Workflow

About workflow of command line runer, it uses 2 types sequence diagram to explain the relationship between different objects
and functions.

* Sequence diagram

![sequence diagram - command runner]

[sequence diagram - command runner]: ../../images/development/cmd_runner_sequence_diagram.drawio.png

From the sequence diagram, you could observe that function ``dispatch_command_processor`` would keep getting the correct
instances of ``CommandProcessor`` to run current command line.

However, how it gets the correct object to process current command line? That's the reason having below activity sequence
diagram to explain that:

* Activity sequence diagram for getting ``CommandProcessor``

![activity sequence diagram - command runner]

[activity sequence diagram - command runner]: ../../images/development/cmd_runner_activity_sequence_diagram.drawio.png

In short, function ``dispatch_command_processor`` would iterate all instances of ``CommandProcessor`` to find the one which
is responsible for current command line.

Now you may have another question: it seems like that it has a ``CommandProcessor`` instance of list to let it find. So what
is the list? When does the list would be generated?

The answers of above would be in next section.
