## With pip <small>for general usage</small> { #with-pip data-toc-label="with pip" }

[**_pip_**](https://pip.pypa.io/en/stable/) is a Python package management tool. We could install all the Python packages
which be managed in [**PyPI**](https://pypi.org/) platform. So we also could install **_PyMock-API_** via pip as below command:

```console
pip install pymock-api
```

However, it may have something problems:

* It would install all the dependencies which may includes something you don't need. 

So it recommends that installs **_PyMock-API_** by pip with option to install the necessary dependencies only.

```console
pip install "pymock-api[<web framework>]"
```

The dependencies which are necessary to install decreases greatly.

!!! note "What the option _web framework_ we could use?"

    **_PyMock-API_** uses the Python web framework to implement the API feature. It means that it would also depend on other
    Python package which for web development. Currrently, it supports 2 frameworks of all popular Python web framerworks
    --- [**_Flask_**] and [**_FastAPI_**]. So the options value we could use are: ``auto``, ``flask`` or ``fastapi``. The 
    option ``auto`` means that it would automatically scan which Python web framework it would use in the current Python 
    runtime environment where the command line tool runs in.

  [**_Flask_**]: https://flask.palletsprojects.com/en/2.3.x/
  [**_FastAPI_**]: https://fastapi.tiangolo.com


## With poetry <small>recommended for Python developer</small> { #with-poetry data-toc-label="with poetry" }

If you're familiar with Python, it strongly recommends that use [**Poetry**] to manage your Python project includes installing
this package.

[**Poetry**]: https://python-poetry.org/docs/

<details markdown="1">
<summary>So what is Poetry ...?</summary>

If you still miss your direction about how to manage your Python project, you must try to use **_Poetry_** to do it. Poetry
is a tool for managing your Python project includes the deeply complex relations of Python dependencies.

Let's quickly demonstrate the general usage of Poetry to you.

If you want to add a new dependency, in the other words, install a new Python package, it doesn't use ``pip``, use ``poetry``
to add it.

```console
poetry add <Python package>
```

How easy it is! Isn't it? It's also easy for removing dependency:

```console
poetry remove <Python package>
```

So what's the difference between **_Poetry_** and **_pip_**? The major difference is **_Poetry_** could be greatly better
to manage your dependencies! Let's consider a scenario. If a package A which depends on pacakge B, it would also install
package B when it installs pacakge A. However, about removing this package, it's a trouble when you use **_pip_** because
**_pip_** won't remove package B when you remove package A! You need to manually remove package B if you want to remove
them clearly. If your project is huge, it's also a big problem of managing your project's dependencies. And the poetry is
a great solution to resolve this issue. Poetry even sorts out the dependencies relations as a tree diagram and illustrate
it as following:

```console
>>> poetry show --tree --without=dev
fastapi 0.95.2 FastAPI framework, high performance, easy to learn, fast to code, ready for production
├── email-validator >=1.1.1
│   ├── dnspython >=2.0.0
│   └── idna >=2.0.0
├── httpx >=0.23.0
│   ├── certifi *
│   ├── httpcore >=0.15.0,<0.18.0
│   │   ├── anyio >=3.0,<5.0
│   │   │   ├── idna >=2.8
...
```

How clear it is! So Poetry is a very powerful tool for manage your Python project.

</details>

The installing command is little different with ``pip`` but be similar:

```console
poetry add pymock-api
```

It also could install necessary parts of dependencies only.

```console
poetry add "pymock-api[<web framework>]"
```

It should add one more dependency **_PyMock-API_** in your configuration _pyproject.toml_.

## With git

If you want to use the latest features of **_PyMock-API_**, you could use ``git`` to clone the project's source code first.

```console
git clone https://github.com/Chisanan232/PyMock-API.git ./pymock-api -b <git branch>
```

!!! note "The dividing rule of git branch"

    **_PyMock-API_** project has been divided into several git branches with different stages:

    ![demonstration](../images/project_process_stages.png)
    
    * develop
        * Git branch: _develop/**_
        * Majot process: All the development should base on this branch to work. The code of this branch always be latest
        but also unstable.
    * pre-release
        * Git branch: _develop/pre-release_
        * Majot process: Summarize all the code from develop branch and all the PR to _release_ branch should be sended
        from this branch. The code in this branch are possible under verify and review so it still not really stable.
    * release
        * Git branch: _release_
        * Majot process: The code which be ready for releasing. All the PR to _master_ branch should be sended from this
        branch. In generally, the features in this branch is stable and ready for releasing.
    * master
        * Git branch: _master_
        * Majot process: The final code to release to PyPI incudes documentation. The code of this branch is stablest and
        it also be same as the code in PyPI.


After source code be ready, you could install it by ``pip``.

```console
pip install -e pymock-api
```

## Verify the command line feature

No matter which way to install **_PyMock-API_**, it must verify whether the command line tool is ready for working or not.

```console
mock-api --help
```

If it outputs some usage info about the command ``mock-api``, congratulation! You could start to enjoy easily and quickly
mock API.
