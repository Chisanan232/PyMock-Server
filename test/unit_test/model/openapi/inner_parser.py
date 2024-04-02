import json
import os
import re

import pytest

from pymock_api.model.openapi._parse import OpenAPIV2Parser


class TestOpenAPIParser:

    def test_initial_parser_with_valid_file(self):
        file_path: str = "./test.json"
        try:
            # Given
            with open(file_path, "a+", encoding="utf-8") as io_stream:
                io_stream.write(json.dumps({"paths": "test API"}))

            # Run target function
            parser = OpenAPIV2Parser(file=file_path)

            # Verify
            assert parser.get_paths() == "test API"
        finally:
            os.remove(file_path)

    def test_initial_parser_with_invalid_file(self):
        # Run target function
        with pytest.raises(FileNotFoundError) as exc_info:
            OpenAPIV2Parser(file="./not_exist.json")

        # Verify
        assert re.search(r".{0,32}not find.{0,32}OpenAPI format configuration", str(exc_info.value), re.IGNORECASE)
