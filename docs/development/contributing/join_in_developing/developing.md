# Developing

Here are some guidelines for developing open source project **_PyMock-Server_**. It's very easy to start because **_PyMock-Server_**
is managed by **Poetry**.


## Requirements for development

[![Supported Versions](https://img.shields.io/pypi/pyversions/fake-api-server.svg?logo=python&logoColor=FBE072)](https://pypi.org/project/fake-api-server)

**_PyMock-Server_** require Python version 3.8 up. Please make sure the Python version in your runtime environment.

???+ tip "Recommended: Use the latest Python version to develop"

    **_PyMock-Server_** only support Python version 3.8 +. If you're user, please make sure you're Python
    version should be newer than version 3.8. However, for developers, it strongly suggests you should
    upgrade your runtime environment Python to the latest version. We should not take too much time to
    develop with older version and the responsibility of the test running with older versions belong to
    CI tool. It does definitely not your job.

On top of that, there are another 2 tools would suggest you to install it: **PyEnv** and **Poetry**.

### **PyEnv** <small> - Python versions management </small>

First of all, you should make sure that you have already installed **PyEnv**.

```console
pyenv --version
```

If you don't, please [install](https://github.com/pyenv/pyenv#installation) it.

**PyEnv** is a great tool for strongly managing so many different Python versions in your runtime environment. With it, you
could very quickly switch to different Python version to developing or troubleshooting with your Python code. That's very
helpful to developers to develop a crossing Python version library or tool.

After checking **PyEnv**, let's check next one tool: **Poetry**:

### **Poetry** <small> - Python project dependency management </small>

```console
poetry --version
```

If you don't [install](https://python-poetry.org/docs/#installation) it, please install it.

**Poetry** is a powerful tool for managing dependencies for Python project. It also could manage many things like other tool's
configuration detail settings.

## Set Python runtime environment

Now, we have installed **PyEnv** and **Poetry**. We can:

* Use **PyEnv** to manage Python versions in our runtime environment.
* Use **Poetry** to manage the dependencies or other tool's configuration settings of our Python project.

From above 2 statements, we also can:

* Use **PyEnv** to control which Python version runtime environment we would use to develop
* Use **Poetry** to configure project dependencies with current Python runtime environment

So let's start to set the latest Python version in current environment.

First, install the latest Python version:

```console
pyenv install <Python version>
```

!!! note "Verify what Python versions you have installed before"

    You could verify the version info by below command:

    ```console
    pyenv versions
    ```

Second, create a virtual environment with the Python version.

It suggests you create a virtual environment with one specific Python version for your project. That could help to let your
project's dependency be independent of your local environment with one specific Python version. In other words, it would be
convenience to create another virtual environment with other different Python version to develop or debug.

```console
pyenv virtualenv <Python version> <virtusl environment name>
```

Let's access to the virtual environment and verify the Python version in it:

```console
pyenv activate <virtusl environment name>
```

Check the Python version:

```console
python --version
```

After we access to virtual environment and verify the Python version, we could install tool **Poetry**:

```console
pip install poetry
```

Don't forget verify the tool function:

```console
poetry --help
```


## Install development dependencies

Now, we have already prepared the runtime environment and tools. And we should be in the virtual environment and tool **Poetry**
has been ready for using. Let's start to install dependencies.

It's very easy to install dependencies for the Python project be managed by **Poetry**. You only run the command line as
following:

```console
poetry install
```

It will take some time to install all dependencies the project needs. After it done, we could verify the dependencies:

```console
poetry run pip list
```

!!! warning "``pip`` in virtual environment vs ``pip`` in Poetry shell"

    The dependencies would be installed in **Poetry shell**, doesn't in virtual environment shell.
    **Poetry** would also help you create a virtual environment to set all configurations of your
    Python project. So if you verify the dependencies in currenct runtime environment directly, it
    is empty. That's why you should check it through command ``poetry run``.


## Verify features

After finish all the above prerequisites, let's try to run the command line feature!

We should activate the command line feature by 2 ways: **run the directory of source code** or **run command line**.

### run the directory of source code

**_PyMock-Server_** has entry point for package. So it could run the folder of source code directly.

=== "Out of Poetry shell"
    
    ```console
    poetry run ./fake_api_server --help
    ```

=== "Within Poetry shell"
    
    ```console
    ./fake_api_server --help
    ```

### run command line

Run the command line directly to be closer in usage as a developers:

=== "Out of Poetry shell"
    
    ```console
    poetry run mock --help
    ```

=== "Within Poetry shell"
    
    ```console
    mock --help
    ```

??? question "How to access into **Poetry** shell"

    You could access into **Poetry** shell as below command:

    ```console
    poetry shell
    ```

Congratulation! Right now you could start to do anything what you want to do of **_PyFake-API-Server_** project!
