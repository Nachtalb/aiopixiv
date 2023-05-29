from typing import Optional

from aiopixiv._pixivobject import PixivObject


class Page(PixivObject):
    """
    This object represents a page of some kind on Pixiv.

    The content of the page may vary, but the implementation of each page like structure
    is the same.

    Attributes:
        next_url (Optional[str]): The next URL for pagination

    Args:
        next_url (Optional[str]): The next URL for pagination
    """

    def __init__(
        self,
        next_url: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.next_url = next_url

        self._id_attrs = (self.next_url,)
