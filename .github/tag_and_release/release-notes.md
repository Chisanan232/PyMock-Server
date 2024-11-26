### 🎉🎊🍾 New feature
<hr>

1. Support parsing version2 (aka Swagger) and version3 OpenAPI document configuration.
2. Support nested data structure about collection data types, i.e., ``list`` or ``dict``, in response.
3. Add new command line argument ``--source-file`` in sub-command line ``pull`` for being more convenience to pull configuration for **_PyMock-API_**.
4. Let sub-command line ``add`` support dividing feature.


### 🛠🐛💣 Bug Fix
<hr>

1. Fix some issues.
   1. It cannot parse finely at the empty body of one specific column in response.
   2. Fix broken tests.
   3. Fix incorrect serializing logic if request parameter or body is empty.
   4. Fix incorrect checking logic at configuration validation in sub-command line ``check``.
   5. Fix the issue about it cannot work finely with argument ``--base-file-path`` in sub-command line ``pull``.


### 🤖⚙️🔧 Improvement
<hr>

1. Upgrade the dependencies.
2. Upgrade the reusable workflows in CI workflow.
3. Extract the logic about initialing test data for testing as modules.


### 📝📑📗Docs
<hr>

1. Update the content for new feature.
