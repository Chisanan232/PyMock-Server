# Software technical details

Software architecture is very important in a production because it's relative the flexibility and extensibility of the production.
So it must have some designs applies to core functions codes.

In **_PyMock-Server_** realm, it can divide to several sections to parse its software architecture:

* Entry point of entire program
    * Runner of command line

* Command line
    * Entire command line - subcommand lines & options
    * Entire command line processors

* Features of command line
    * Functional - options ``--config``
    * The sub-command line ``rest-server run``

Above all are some parts which have value or more complex to explain their details to developers.
