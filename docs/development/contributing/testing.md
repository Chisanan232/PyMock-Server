# Testing

About the testing, **_PyMock-API_** has some prerequisites or rules of it. **_PyMock-API_** has 2 types test: unit test and
integration test. Unit test are in directory _test/unit_test_ and integration test are in directory _test/integration_test_.


## Requirements for testing

**_PyMock-API_** uses test framework [**_PyTest_**]. So please make sure its tool ``pytest`` could work finely in your current
runtime environment for development.

[**_PyTest_**]: https://docs.pytest.org/

=== "Out of Poetry shell"
    
    ```console
    poetry run pytest --version
    ```

=== "Within Poetry shell"
    
    ```console
    pytest --version
    ```

Apart from **_PyTest_**, **_PyMock-API_** also use another dependencies and some of them is **_PyTest_** plugin.

* **_coverage_**

    For recording, calculating the test coverage of source code and generating report about it.

* **_pytest-cov_**

    Let **_PyTest_** supports all feature of **_coverage_**.

* **_pytest-rerunfailures_**

    Let **_PyTest_** supports re-run feature.

Please refer to the configuration [_pyproject.toml_] if you need.

[_pyproject.toml_]: https://github.com/Chisanan232/PyMock-API/blob/master/pyproject.toml


## Run test

It has 2 ways to run test when you develop **_PyMock-API_**.

### Specific test module

If you're developing one independent feature and only want to run a single module test, you just need to run ``pytest`` with the
file path.

=== "Out of Poetry shell"
    
    ```console
    poetry run pytest <.py file path>
    ```

=== "Within Poetry shell"
    
    ```console
    pytest <.py file path>
    ```

If you just want to one specific test item, you could use option ``-k``.

=== "Out of Poetry shell"
    
    ```console
    poetry run pytest <.py file path> -k 'test_item'
    ```

=== "Within Poetry shell"
    
    ```console
    pytest <.py file path> -k 'test_item'
    ```

!!! note "Run test more efficiency"

    In default from the **_PyTest_** configuration of **_PyMock-API_**, it would
    re-run the test 3 times if it get fail at running the test. For being convenience
    at developing, you could set value as ``0`` at option ``--reruns``.

    ```console
    pytest <.py file path> --reruns 0
    ```


### All the one specific test type tests

After you finish development of one or more features, it suggests you to run all tests to guarantee that you don't break up
the code. If you want to run all tests, you would need to use shell script _scripts/run_all_tests.sh_ to reach it. The shell
script accept one argument --- test type. You have 3 types value could use:

* all-test

    Run entire all tests under directory _test_.

* unit-test

    Run all unit tests and the test modules are in directory _test/unit_test_.

* integration-test

    Run all integration tests and the test modules are in directory _test/integration_test_.

=== "Out of Poetry shell"
    
    ```console
    poetry run bash ./scripts/run_all_tests.sh <test type>
    ```

=== "Within Poetry shell"
    
    ```console
    bash ./scripts/run_all_tests.sh <test type>
    ```


## How to add test sub-package?

For clean file naming, **_PyMock-API_** won't add character ``test`` at file naming. It would use shell script _scripts/run_all_tests.sh_
to control which test module it should run. 

Shell script _scripts/run_all_tests.sh_ would use the test sub-package path to get all test modules in it. For example, it has
a test sub-package _A_, and there are 3 test modules _aaa.py_, _bbb.py_ and _ccc.py_ in it. It needs to set the test sub-package
path _A_ in the shell script, and it would help us to get all paths of modules _test/A/aaa.py_, _test/A/bbb.py_ and _test/A/ccc.py_
to us.

So if we have new test sub-package, it needs to add the new test sub-package path in shell scripts to let _scripts/run_all_tests.sh_
could get the new test module to run.

The new test sub-package in different test type, then it should add the path to mapping shell script.

* _scripts/ci/get-unit-test-paths.sh_

    The shell script for getting all unit test modules which are in directory _test/unit_test_.

* _scripts/ci/get-integration-test-paths.sh_

    The shell script for getting all integration test modules which are in directory _test/integration_test_..

Below demonstrate how to add new test sub-package path in shell script.

```shell

# Some shell ...

# The variable for saving all test modules in the new test sub-package
declare -a new_test_subpkg_tests

# Some shell ...

getalltests() {
    # Some shell ...

    # The condition for identifying the test sub-package path
    elif echo "$1" | grep -q "new_test_subpkg";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        new_test_subpkg_tests=${alltestpaths[@]}

# Some shell ...

# The new test sub-package path
new_test_subpkg_path=./test/unit_test/new_test_subpkg

# Some shell ...

# Run the function to get all the test module paths
getalltests $new_test_subpkg_path

# Combine all paths as return value
dest=( "${init_tests[@]} ${utils_tests[@]} ${model_tests[@]} ${server_tests[@]} ${server_sgi_tests[@]} ${new_test_subpkg_tests[@]}" )

# Some shell ...
```

You will see the running result includes the new path of all test modules which are in new test sub-package.

```console
>>> bash ./scripts/ci/<the shell script what you modify> 'unix'
```

!!! note "Argument of shell script"

    It has an argument of the shell script about what OS the current runtime environment is in.

    * ``unix``

        For Unix OS or MacOS.

    * ``windows``

        For Windows OS.
