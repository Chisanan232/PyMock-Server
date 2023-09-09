# Subcommand ``get`` usage

Getting detail info with specific conditions for comprehensive inspection of configuration.

```console
>>> mock-api get <option>
```


## ``--config-path`` or ``-p`` <config file path\>

Set the configuration file path.

It receives a value about the configuration file path and its default value is ``api.yaml``.


## ``--show-detail`` or ``-s``

Get the configuration details if activate this command line option. Nor **_PyMock-API_** would only tell you the setting 
with the API exists without any info.

It doesn't accept any value.


## ``--show-as-format`` or ``-f`` <output-info-format\>

Display the configuration details as one specific format.

It receives a string value about format of configuration details, and it has default value ``text``. All the values you
could use at this command line option are:

  * ``text``
  * ``yaml``
  * ``json``


## ``--api-path`` or ``-a`` <API path\>

The condition uses API path for getting the relative configuration which URL setting is the API path.

It receives a string value about the API path.


## ``--http-method`` or ``-m`` <HTTP method\>

The condition uses HTTP method of API path for getting the relative configuration which URL setting is the API path and
HTTP method setting is same as the option value.

It receives a string value about the HTTP method of API path.
