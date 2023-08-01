# Subcommand ``sample`` usage

Doing something operations about configuration or its content.

```console
>>> mock-api sample <option>
```


## ``--print-sample`` or ``-p``

Show the sample configuration which could be used directly by **_PyMock-API_**.

It doesn't accept any value.


## ``--generate-sample`` or ``-g``

Generating the sample configuration as a ``.yaml`` file. The configuration content is same as the output of running result
with option ``--print-sample``.

It doesn't accept any value.


## ``--output`` or ``-o`` <output-file-path\>

Generating the sample configuration to the target output file path.

It receives a value about the configuration file path, and it doesn't have default value. It would exit the program and
output error message if it doesn't have value of this option when using option ``--generate-sample``.
