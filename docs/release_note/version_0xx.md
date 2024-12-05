# Version 0.X.X

## 0.2.0

### 🎉🎊🍾 New feature

1. Support parsing version2 (aka Swagger) and version3 OpenAPI document configuration.
2. Support nested data structure about collection data types, i.e., ``list`` or ``dict``, in response.
3. Add new command line argument ``--source-file`` in sub-command line ``pull`` for being more convenience to pull configuration for **_PyMock-API_**.
4. Let sub-command line ``add`` support dividing feature.


### 🛠🐛💣 Bug Fix

1. Fix some issues.
   1. It cannot parse finely at the empty body of one specific column in response.
   2. Fix broken tests.
   3. Fix incorrect serializing logic if request parameter or body is empty.
   4. Fix incorrect checking logic at configuration validation in sub-command line ``check``.
   5. Fix the issue about it cannot work finely with argument ``--base-file-path`` in sub-command line ``pull``.


### 🤖⚙️🔧 Improvement

1. Upgrade the dependencies.
2. Upgrade the reusable workflows in CI workflow.
3. Extract the logic about initialing test data for testing as modules.


### 📝📑📗Docs

1. Update the content for new feature.


## 0.1.0

### 🎉🎊🍾 New feature

1. Provide command line interface ``mock-api`` for mocking HTTP server.

    ```shell
    usage: mock-api [SUBCOMMAND] [OPTIONS]
    
    A Python tool for mocking APIs by set up an application easily. PyMock-API bases on Python web framework to set up application, i.e., you could select using *flask* to set up application to mock APIs.
    
    options:
      -h, --help            show this help message and exit
      -v, --version         The version info of PyMock-API.
    
    Subcommands:
    
      {run,sample,add,check,get,pull}
        run                 Set up APIs with configuration and run a web application to mock them.
        sample              Quickly display or generate a sample configuration helps to use this tool.
        add                 Something processing about configuration, i.e., generate a sample configuration or validate configuration content.
        check               Check the validity of *PyMock-API* configuration.
        get                 Do some comprehensive inspection for configuration.
        pull                Pull the API details from one specific source, e.g., Swagger API documentation.
    ```

2. Provide [documentation](https://chisanan232.github.io/PyMock-Server/) for details of the project.
