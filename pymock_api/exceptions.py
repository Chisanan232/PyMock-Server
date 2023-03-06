from typing import List


class FileFormatNotSupport(RuntimeError):
    def __init__(self, valid_file_format: List[str]):
        self._valid_file_format = valid_file_format

    def __str__(self):
        return f"It doesn't support reading '{', '.join(self._valid_file_format)}' format file."
