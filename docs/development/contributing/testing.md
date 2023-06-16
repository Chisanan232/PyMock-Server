# Testing

content ...


## Requirements for testing

content ...

=== "Out of Poetry shell"
    
    ```console
    poetry run pytest --version
    ```

=== "Within Poetry shell"
    
    ```console
    pytest --version
    ```

content ...


## Run specific test module

content ...

=== "Out of Poetry shell"
    
    ```console
    poetry run pytest <.py file path>
    ```

=== "Within Poetry shell"
    
    ```console
    pytest <.py file path>
    ```

content ...

!!! note "Run test more efficiency"

    content ...

    ```console
    pytest <.py file path> --reruns 0
    ```

## Run all tests of one specific test type

content ...

=== "Out of Poetry shell"
    
    ```console
    poetry run bash ./scripts/run_all_tests.sh <test type>
    ```

=== "Within Poetry shell"
    
    ```console
    bash ./scripts/run_all_tests.sh <test type>
    ```

content ...
