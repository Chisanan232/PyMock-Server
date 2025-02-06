# Subcommand ``check`` usage

Check the validity of configuration content.

```console
>>> fake rest-server check <option>
```


## ``--config-path`` or ``-p`` <config-file-path\>

Set the target configuration file for checking.

It receives a value about the configuration file path and its default value is ``api.yaml``.


## ``--stop-if-fail`` <Boolean value\>

If it's ``True``, it would terminate directly if it detects any issue. If it's ``False``, it would detect and show all issues
and exit program with exit code _1_ finally.

It receives a boolean value and default value is ``False``.


## ``--swagger-doc-url`` or ``-s`` <Swagger API document URL or host address\>

The URL or host address of Swagger API document. It would compare current API config all details (which be set by option ``--config-path``)
with the API details of this Swagger API document.

It receives a string value.


## ``--check-entire-api``

If it's ``True``, check the entire API settings includes API path, HTTP method and request parameters.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.


## ``--check-api-path``

If it's ``True``, check whether the API exist or not by URL path.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.


## ``--check-api-http-method``

If it's ``True``, check the HTTP method of API.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.


## ``--check-api-parameters``

If it's ``True``, check the request parameters of API.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.
