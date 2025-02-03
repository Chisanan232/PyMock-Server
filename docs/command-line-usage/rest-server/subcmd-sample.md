# Subcommand ``sample`` usage

Doing something operations about configuration or its content.

```console
>>> mock rest-server sample <option>
```


## ``--print-sample`` or ``-p``

Show the sample configuration which could be used directly by **_PyFake-API-Server_**.

It doesn't accept any value.


## ``--generate-sample`` or ``-g``

Generating the sample configuration as a ``.yaml`` file. The configuration content is same as the output of running result
with option ``--print-sample``.

It doesn't accept any value.


## ``--output`` or ``-o`` <output-file-path\>

Generating the sample configuration to the target output file path.

It receives a value about the configuration file path, and it doesn't have default value. It would exit the program and
output error message if it doesn't have value of this option when using option ``--generate-sample``.


## ``--sample-config-type`` or ``-t`` <sample config type\>

Which sample configuration it should generate. Currently, it has 4 types:

* ``all``

    The sample configuration which has 3 mocked APIs about each sample of ``response_as_str``, ``response_as_json`` and ``response_with_file``.

* ``response_as_str``

    The sample configuration which has sample mocked API with response returns string value directly.

* ``response_as_json``

    The sample configuration which has sample mocked API with response returns JSON format value.

* ``response_with-file``

    The sample configuration which has sample mocked API with response as a file path. It would return the file content as
    response.

It receives a string value about the sample type and its default value is ``all``.
