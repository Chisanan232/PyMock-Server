import inspect
import json
from functools import wraps
from typing import Any, Callable, Type

from .._file_utils import _BaseConfigFactory, file

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper  # type: ignore

from .._values import _YouTube_API_Content


class run_test:
    @classmethod
    def with_file(cls, factory: Type[_BaseConfigFactory]) -> Callable:
        assert factory, "It must set a way to operate configuration file."
        if inspect.isclass(factory) and issubclass(factory, _BaseConfigFactory):
            config_file = factory()
        else:
            assert False, "Decorator's argument cannot accept None value in code usage."

        def _wrap_func(function: Callable) -> Callable:
            @wraps(function)
            def _(self, *args, **kwargs) -> Any:
                # Ensure that it doesn't have file
                config_file.delete()
                # Create the target file before run test
                config_file.generate()
                file.write(
                    path="youtube.json", content=_YouTube_API_Content, serialize=lambda content: json.dumps(content)
                )

                try:
                    # Run the test item
                    function(self, *args, **kwargs)
                finally:
                    # Delete file finally
                    config_file.delete()
                    file.delete("youtube.json")

            return _

        return _wrap_func
