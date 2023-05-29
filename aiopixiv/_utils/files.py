#!/usr/bin/env python
from pathlib import Path
from typing import IO, Optional

from aiopath import AsyncPath

from aiopixiv._utils.types import FileInput


async def load_file(obj: FileInput) -> bytes:
    """
    Read the given file asynchronously
    """
    from aiopixiv.request._inputfile import InputFile

    match obj:
        case bytes():
            return obj
        case str():
            return obj.encode("utf-8")
        case Path():
            return await load_file(AsyncPath(obj))
        case AsyncPath():  # type: ignore[misc]
            return await obj.read_bytes()
        case InputFile():
            return await obj.file_content()
        case IO():
            return obj.read()
        case _:
            raise TypeError(f"Unsupported file input type: {type(obj)}")


def get_filename(obj: FileInput) -> Optional[str]:
    if isinstance(obj, (Path, AsyncPath)):
        return obj.name
    return None
