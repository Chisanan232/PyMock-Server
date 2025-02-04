# Option ``--config`` - file operation

Here focus on a small part --- a feature of one specific option ``--config`` under sub-command ``run``.

## UML

<iframe frameborder="0" style="width:100%;height:780px;" src="https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=PyMock-Server.drawio&page-id=UBu_mQ72ApCV_EWYisV4#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1hq5q_Eaa8O48HgSEO8stAbWoS4HnwxEm%26export%3Ddownload"></iframe>

* Object ``MockHTTPServer`` uses function ``load_config`` to get all detail settings.
* Data object ``APIConfig`` provides function to read and deserialize the configuration file content.
* Currently, it only supports parsing YAML file by object ``YAML``.

## Extension

Here demonstrate how to extend this feature to parse other file formatter.

* File operation

If you want to use other file formatter, e.g., JSON, you could extend the base class of file operation _``BaseFileOperation``
to implement needed features.

```python
# In module fake_api_server.command.options

# ... some code

class JSON(_BaseFileOperation):
    def read(self):
        # Read the configuration file content

    def write(self, path: str, config: Union[str, dict]) -> None:
        # Write data into file

    def serialize(self, config: dict) -> str:
        # Serialize dat object to string value
```

Because currently it won't have option in command line to control which way it should use to serialize or deserialize configuration
file, so we need to manually modify the code to use it.

```python hl_lines="10"
# In module fake_api_server.model.api_config

class APIConfig(_Config):
    """*The entire configuration*"""

    _name: str = ""
    _description: str = ""
    _apis: Optional[MockAPIs]

    _configuration: _BaseFileOperation = JSON()

    def __init__(self, name: str = "", description: str = "", apis: Optional[MockAPIs] = None):
        self._name = name
        # ... some code
```

Finally, we could use JSON type file as our configuration formatter.

```console
>>> mock -c ./api.json
```
