from typing import Optional

from aiopixiv._pixivobject import PixivObject


class Tag(PixivObject):
    """
    This object represents a Pixiv tag.

    Args:
        name (str): The name of the tag.
        translated_name (Optional[str]): The translated name of the tag.

    Attributes:
        name (str): The name of the tag.
        translated_name (Optional[str]): The translated name of the tag.
    """

    __slots__ = ("name", "translated_name")

    def __init__(
        self,
        name: str,
        translated_name: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.name = name
        self.translated_name = translated_name

        self._id_attrs = (self.name,)
