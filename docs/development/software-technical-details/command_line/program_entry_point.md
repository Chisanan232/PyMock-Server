# Program entry point - command line runner

The entry point of **_PyFake-API-Server_** command line tool. Its actually entry point is calling the function ``run`` in module
``fake_api_server.runner``.

## UML

<iframe frameborder="0" style="width:100%;height:573px;" src="https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=PyMock-Server.drawio&page-id=MX22taNxn-K2Fd3PBEBv#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1hq5q_Eaa8O48HgSEO8stAbWoS4HnwxEm%26export%3Ddownload"></iframe>

* About the function which would be run as entry point ``run``, it's a running logic of object ``CommandRunner``.
* Object ``CommandRunner`` would keep instance of ``ArgumentParser`` and ``CommandProcessor`` to parse command line and run
core logic of the current sub-command.
* Object ``CommandRunner`` would use function ``dispatch_command_processor`` to get the correct instance to handle current
command line.

## Workflow

About workflow of command line runer, it uses 2 types sequence diagram to explain the relationship between different objects
and functions.

* Sequence diagram

<iframe frameborder="0" style="width:100%;height:350px;" src="https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=PyMock-Server.drawio&page-id=xViBYGax6CRM-3lJNWmd#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1hq5q_Eaa8O48HgSEO8stAbWoS4HnwxEm%26export%3Ddownload"></iframe>

From the sequence diagram, you could observe that function ``dispatch_command_processor`` would keep getting the correct
instances of ``CommandProcessor`` to run current command line.

However, how it gets the correct object to process current command line? That's the reason having below activity sequence
diagram to explain that:

* Activity sequence diagram for getting ``CommandProcessor``

<iframe frameborder="0" style="width:70%;height:700px;" src="https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=PyMock-Server.drawio&page-id=OGFfPSg3NHsL9dp7TJ5e#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1hq5q_Eaa8O48HgSEO8stAbWoS4HnwxEm%26export%3Ddownload"></iframe>

In short, function ``dispatch_command_processor`` would iterate all instances of ``CommandProcessor`` to find the one which
is responsible for current command line.

Now you may have another question: it seems like that it has a ``CommandProcessor`` instance of list to let it find. So what
is the list? When does the list would be generated?

The answers of above would be in next section.
