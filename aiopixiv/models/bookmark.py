from typing import TYPE_CHECKING, List, Optional

from aiopixiv._pixivobject import PixivObject
from aiopixiv._utils.types import JSONDict

if TYPE_CHECKING:
    from aiopixiv._api import PixivAPI


class BookmarkDetailTag(PixivObject):
    """
    A model for representing the tags associated with bookmark.

    Attributes:
        name (str): The name of the tag.
        is_registered (bool): Whether the tag is registered for the illustration.

    Args:
        name (str): The name of the tag.
        is_registered (bool): Whether the tag is registered for the illustration.
    """

    def __init__(
        self,
        name: str,
        is_registered: bool,
    ) -> None:
        super().__init__()

        self.name = name
        self.is_registered = is_registered

        self._id_attrs = (self.name,)


class BookmarkDetail(PixivObject):
    """
    A model for representing the response of the BookmarkDetail API.

    Attributes:
        is_bookmarked (bool): Whether the illustration is bookmarked.
        tags (List[IllustBookmarkDetailTag]): A list of tags associated with the illustration's bookmark details.
        restrict (str): The restriction level for the illustration.

    Args:
        is_bookmarked (bool): Whether the illustration is bookmarked.
        tags (List[IllustBookmarkDetailTag]): A list of tags associated with the illustration's bookmark details.
        restrict (str): The restriction level for the illustration.
    """

    def __init__(
        self,
        is_bookmarked: bool,
        tags: List[BookmarkDetailTag],
        restrict: str,
    ) -> None:
        super().__init__()

        self.is_bookmarked = is_bookmarked
        self.tags = tags
        self.restrict = restrict

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["BookmarkDetail"]:
        data = cls._parse_data(data)

        if not data:
            return None

        data["tags"] = BookmarkDetailTag.de_list(data.pop("tags"), client)

        return super().de_json(data, client)
