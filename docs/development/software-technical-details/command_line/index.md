# Command line

Here is the detail information about software development includes software architecture, how it works by sequence diagram, etc.

It focuses on command line itself, doesn't care other parts like the process or component of the specific command line.
So all the demonstrations in this section would use the minimum level to implement for the parts.

About command line software architecture (also means modules file structure) in **_PyMock-Server_** project, each subcommand
line has their own sub-package and also has 3 necessary modules in the sub-package: **_option_**, **_process_** and **_component_**.

* **_option_**

    This module focus on what options it would have of the specific subcommand line.

* **_process_**

    This module controls how it should parse the subcommand line arguments and what component it should use to handle
    the core logic of running the subcommand line.

* **_component_**

    This module is the core implementation about what thing it would do when user runs the subcommand line with specific
    arguments.

So if you would add new subcommand line. Please remember its modules structure must follow above rules and implement their
own logic.
