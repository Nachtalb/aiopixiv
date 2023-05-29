from __future__ import annotations

from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Dict, Tuple, Union

from aiopath import AsyncPath

if TYPE_CHECKING:
    from aiopixiv.request._inputfile import InputFile

JSONDict = Dict[str, Any]
"""Dictionary containting response from Pixiv"""

FieldTuple = Tuple[str, bytes, str]
"""Alias for return type of `InputFile.field_tuple()`."""
UploadFileDict = Dict[str, FieldTuple]
"""Dictionary containing file data to be uploaded to the API."""


FileLike = Union[IO[bytes], "InputFile"]
"""Either a bytes-stream (e.g. open file handler) or a InputFile."""

FilePath = Union[str, Path, AsyncPath]
"""A filepath either as string, as pathlib.Path or aiopath.AsyncPath object."""

FileInput = Union[FilePath, FileLike, bytes, str]
"""Valid input for passing files to Pixiv. Either a file id as string, a file like object,
a local file path as string, pathlib.Path, aiopath.AsyncPath or the file contents as bytes."""
