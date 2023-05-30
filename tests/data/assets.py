from aiopath import AsyncPath

from aiopixiv._utils.types import FilePath

ASSETS = AsyncPath(__file__).parent / "assets/"


def get_asset(name: FilePath) -> AsyncPath:
    name = AsyncPath(name)

    if name.is_relative_to(ASSETS):
        return name
    return ASSETS / name


async def read_asset(file: FilePath) -> bytes:
    content: bytes = await get_asset(file).read_bytes()
    return content
