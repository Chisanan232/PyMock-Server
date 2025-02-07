### 🎉 New feature

1. Support new properties for customizing the values in request or response.
   1. ``format``: setting the format of value how it should be in request or return in response.
   2. ``variables``: for reusable usage in formatting value.
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

1. Rename the Python package and project again as **_PyFake-API-Server_** to avoid similar project naming issue in PyPI
2. Improve the CD workflows which would only br triggered by updating version info.
3. Let the error message to be more clear and readable for incorrect usage.
4. Let the version info to be more readable and detail.


### 📑 Docs

1. Update the content for all changes.
2. Import the versioning feature into documentation.


### 🤖 Upgrade dependencies

1. Upgrade the Python dependencies.
2. Upgrade pre-commit dependencies.
3. Upgrade the CI reusable workflows.
   1. Upgrade SonarQube and update its configuration
   2. Update the usage because upgrading the artifact actions

### 🚮Deprecate

1. Deprecate and remove version 0.3.0 because it has multiple issue, and it cannot upload same version file to PyPI.
