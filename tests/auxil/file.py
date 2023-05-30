from typing import List

from aiopath import AsyncPath

from aiopixiv._utils.types import FilePath


async def glob_dir(dir: FilePath, glob: str = "*") -> List[AsyncPath]:
    dir = AsyncPath(dir)
    paths = []
    async for path in dir.glob(glob):
        paths.append(path)
    return paths
