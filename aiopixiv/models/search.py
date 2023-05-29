from typing import TYPE_CHECKING, List, Optional

from aiopixiv._utils.types import JSONDict
from aiopixiv.models.illust import Illust, Illusts
from aiopixiv.models.novel import Novel, Novels
from aiopixiv.models.tag import Tag
from aiopixiv.models.user import User, Users

if TYPE_CHECKING:
    from aiopixiv._api import PixivAPI


class TrendingTag(Tag):
    """
    This object represents A Pixiv tag when searching for trending illustrations of said tag.

    Attributes:
        tag (str): The name of the trending tag.
        translated_name (Optional[str]): The translated name of the tag, if available.
        illust (Illust): The illustration associated with the trending tag.

    Args:
        tag (str): The name of the trending tag.
        translated_name (Optional[str]): The translated name of the tag, if available.
        illust (Illust): The illustration associated with the trending tag.
    """

    def __init__(
        self,
        name: str,
        illust: Illust,
        translated_name: Optional[str] = None,
    ) -> None:
        super().__init__(name, translated_name)

        self.illust = illust

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["TrendingTag"]:
        """See `PixivObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["illust"] = Illust.de_json(data.pop("illust", None), client)
        return super().de_json(data=data, client=client)


class SearchIllustResult(Illusts):
    """
    This object represents the illustration search results.

    Attributes:
        illusts (List[Illust]): A list of illustrations that match the search query.
        next_url (Optional[str]): The URL for the next page of search results, if available.
        search_span_limit (int): The search span limit for the query.

    Args:
        illusts (List[Illust]): A list of illustrations that match the search query.
        next_url (Optional[str]): The URL for the next page of search results, if available.
        search_span_limit (int): The search span limit for the query.
    """

    def __init__(
        self,
        illusts: List[Illust],
        search_span_limit: int,
        next_url: Optional[str] = None,
    ) -> None:
        super().__init__(illusts, next_url)

        self.search_span_limit = search_span_limit


class SearchUserResult(Users):
    """
    A model for representing the response of the SearchUser API.

    Attributes:
        users (List[User]): A list of userrations that match the search query.
        next_url (Optional[str]): The URL for the next page of search results, if available.
        search_span_limit (int): The search span limit for the query.

    Args:
        users (List[User]): A list of userrations that match the search query.
        next_url (Optional[str]): The URL for the next page of search results, if available.
        search_span_limit (int): The search span limit for the query.
    """

    def __init__(
        self,
        users: List[User],
        search_span_limit: int,
        next_url: Optional[str] = None,
    ) -> None:
        super().__init__(users, next_url)

        self.search_span_limit = search_span_limit


class SearchNovelResult(Novels):
    """
    A model for representing the response of the SearchNovel API.

    Attributes:
        novels (List[Novel]): A list of novelrations that match the search query.
        next_url (Optional[str]): The URL for the next page of search results, if available.
        search_span_limit (int): The search span limit for the query.

    Args:
        novels (List[Novel]): A list of novelrations that match the search query.
        next_url (Optional[str]): The URL for the next page of search results, if available.
        search_span_limit (int): The search span limit for the query.
    """

    def __init__(
        self,
        novels: List[Novel],
        search_span_limit: int,
        next_url: Optional[str] = None,
    ) -> None:
        super().__init__(novels, next_url)

        self.search_span_limit = search_span_limit
