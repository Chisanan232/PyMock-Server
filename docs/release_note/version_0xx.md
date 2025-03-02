# Version 0.X.X

## 0.4.1

### 🎉 New feature

1. Support running fake server process in background and redirect the access log to the specific log file.
   1. ``--daemon``: daemonize the fake server process.
   2. ``--access-log-file``: redirect the fake server access log to the specific file.


### 📑 Docs

1. Update the content for new command line options.


## 0.3.0

### 🎉 New feature

1. Support new properties for customizing the values in request or response.
   1. ``Format``: setting the format of value how it should be in request or return in response.
   2. ``Variable``: for reusable usage in formatting value.
   3. ``size``: setting the value size. If it's ``str`` type, this is the length limitation; if it's ``int`` or other numeric type value, this is the value limitation.
   4. ``digit``: setting the decimal policy.
2. Support setting the format properties in template section.
3. Re-fine the command line interface to be more friendly and more readable in usage.


### 🪲 Bug Fix

1. Fix broken tests in some specific Python versions.
2. Fix the broken CI workflow about auto-merge the upgrade dependencies PRs which has been approved.


### ♻️ Refactor

1. Re-fine the pure data into data models in data processing of handling API documentation.
2. Adjust the modules structure about core logic of API server processing with classifying by API server type.
3. Refactor the modules structure of command line options, processors and components.
4. Refactor the enum objects into the module or sub-package which are deeply relative with their meaning.
5. Extract the file operation logic into new sub-package in __util_.


### 🍀 Improvement

1. Improve the CD workflows which would only br triggered by updating version info.
2. Let the error message to be more clear and readable for incorrect usage.
3. Let the version info to be more readable and detail.


### 📑 Docs

1. Update the content for all changes.
2. Import the versioning feature into documentation.


### 🤖 Upgrade dependencies

1. Upgrade the Python dependencies.
2. Upgrade pre-commit dependencies.
3. Upgrade the CI reusable workflows.


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
