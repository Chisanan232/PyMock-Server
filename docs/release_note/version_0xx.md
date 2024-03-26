# Version 0.X.X

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

2. Provide [documentation](https://chisanan232.github.io/PyMock-API/) for details of the project.
