#!/usr/bin/env python
import mimetypes
from typing import IO, Optional, Union

from aiopixiv._utils.files import get_filename, load_file
from aiopixiv._utils.types import FieldTuple

_DEFAULT_MIME_TYPE = "application/octet-stream"


class InputFile:
    """
    This object is a wrapper for easier handling with files in the api.

    Args:
        obj (file object | bytes | str): An open file descriptor or the files
            content as bytes or string.
        filename (str, optional): Filename for this InputFile when uploaded.

    Attributes:
        filename (str): Filename for the file to be sent.
        mimetype (str): The mimetype inferred from the file to be sent.
    """

    __slots__ = ("filename", "_file_obj", "_file_content", "mimetype")

    def __init__(
        self,
        obj: Union[IO[bytes], bytes, str],
        filename: Optional[str] = None,
    ):
        self._file_obj = obj

        if isinstance(obj, bytes):
            self._file_content: bytes = obj
        elif isinstance(obj, str):
            self._file_content = obj.encode("utf-8")
        else:
            self._file_content = b""
            filename = filename or get_filename(obj)

        if filename:
            self.mimetype: str = mimetypes.guess_type(filename, strict=False)[0] or _DEFAULT_MIME_TYPE
        else:
            self.mimetype = _DEFAULT_MIME_TYPE

        self.filename: str = filename or self.mimetype.replace("/", ".")

    async def field_tuple(self) -> FieldTuple:
        """
        Field tuple representing the contents of the file for upload.

        Returns:
            Tuple[str, bytes, str]:
        """
        return self.filename, await self.file_content(), self.mimetype

    async def file_content(self) -> bytes:
        if not self._file_content:
            self._file_content = await load_file(self._file_obj)
        return self._file_content
