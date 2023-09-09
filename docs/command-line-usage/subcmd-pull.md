# Subcommand ``pull`` usage

If it has already had API documentation, e.g., OpenAPI format (aka Swagger API), provides the API details, you could use
``pull`` feature to fetch it as **_PyMock-API_** format configuration and set up HTTP server for mocking API easily and 
quickly.

??? note "Why we need sub-command line ``pull``?"

    Let's consider one scenario, the system has already provide service for a while 
    and it has so many APIs which have already be used awhile. However, you want to 
    import this tool for Font-End site development, but it's too hard to configure 
    all existing APIs into **_PyMock-API_** configuration. At this time, ``pull`` 
    feature could give you a hand to handle it easily and quickly.


```console
>>> mock-api pull <option>
```


## ``--source`` or ``-s`` <API document URL\>

Set the source where it should try to get the API documentation configuration and convert it as **_PyMock-API_** format
configuration.

It receives a string value about the host address or URL path.


## ``--base-url``

Set the base URL for deserialization of API documentation configuration.

It receives a string value about the base URL path.


## ``--config-path`` or ``-c`` <config file path\>

The file path for saving configuration which be fetched and be deserialized from the API documentation configuration to 
**_PyMock-API_** format.

It receives a string value about the configuration file path.
