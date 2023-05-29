from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from aiopixiv._pixivobject import PixivObject
from aiopixiv._utils.types import JSONDict
from aiopixiv.models.page import Page
from aiopixiv.models.privacy import PrivacyPolicy
from aiopixiv.models.tag import Tag
from aiopixiv.models.urls import ImageUrls
from aiopixiv.models.user import User

if TYPE_CHECKING:
    from aiopixiv._api import PixivAPI


class NovelTag(Tag):
    """
    A NovelTag model for representing the tags associated with a novel.

    Attributes:
        name (str): The name of the tag.
        translated_name (Optional[str]): The translated name of the tag, if available.
        added_by_uploaded_user (bool): Whether the tag was added by the user who uploaded the novel.

    Args:
        name (str): The name of the tag.
        translated_name (Optional[str]): The translated name of the tag, if available.
        added_by_uploaded_user (bool): Whether the tag was added by the user who uploaded the novel.
    """

    def __init__(
        self,
        name: str,
        added_by_uploaded_user: bool,
        translated_name: Optional[str] = None,
    ) -> None:
        super().__init__(name, translated_name)

        self.added_by_uploaded_user = added_by_uploaded_user


class NovelSeries(PixivObject):
    """
    A NovelSeries model for representing the series a novel belongs to.

    Attributes:
        id (int): The series unique identifier.
        title (str): The title of the series.

    Args:
        id (int): The series unique identifier.
        title (str): The title of the series.
    """

    def __init__(
        self,
        id: int,
        title: str,
    ) -> None:
        super().__init__()

        self.id = id
        self.title = title

        self._id_attrs = (self.id,)


class Novel(PixivObject):
    """
    A Novel model for representing a novel.

    Attributes:
        id (int): The novel's unique identifier.
        title (str): The title of the novel.
        caption (str): The novel's caption.
        restrict (int): The novel's restriction level.
        x_restrict (int): The novel's x-restriction level.
        is_original (bool): Whether the novel is an original work.
        image_urls (ImageUrls): The image URLs associated with the novel.
        create_date (datetime): The date the novel was created.
        tags (List[NovelTag]): A list of tags associated with the novel.
        page_count (int): The number of pages in the novel.
        text_length (int): The length of the novel's text.
        user (User): The user who created the novel.
        series (Optional[NovelSeries]): The series the novel belongs to, if available.
        is_bookmarked (bool): Whether the novel is bookmarked.
        total_bookmarks (int): The total number of bookmarks on the novel.
        total_view (int): The total number of views on the novel.
        visible (bool): Whether the novel is visible.
        total_comments (int): The total number of comments on the novel.
        is_muted (bool): Whether the novel is muted.
        is_mypixiv_only (bool): Whether the novel is only visible to myPixiv users.
        is_x_restricted (bool): Whether the novel is x-restricted.
        novel_ai_type (int): The novel's AI type.

    Args:
        id (int): The novel's unique identifier.
        title (str): The title of the novel.
        caption (str): The novel's caption.
        restrict (int): The novel's restriction level.
        x_restrict (int): The novel's x-restriction level.
        is_original (bool): Whether the novel is an original work.
        image_urls (ImageUrls): The image URLs associated with the novel.
        create_date (datetime): The date the novel was created.
        tags (List[NovelTag]): A list of tags associated with the novel.
        page_count (int): The number of pages in the novel.
        text_length (int): The length of the novel's text.
        user (User): The user who created the novel.
        series (Optional[NovelSeries]): The series the novel belongs to, if available.
        is_bookmarked (bool): Whether the novel is bookmarked.
        total_bookmarks (int): The total number of bookmarks on the novel.
        total_view (int): The total number of views on the novel.
        visible (bool): Whether the novel is visible.
        total_comments (int): The total number of comments on the novel.
        is_muted (bool): Whether the novel is muted.
        is_mypixiv_only (bool): Whether the novel is only visible to myPixiv users.
        is_x_restricted (bool): Whether the novel is x-restricted.
        novel_ai_type (int): The novel's AI type.
    """

    def __init__(
        self,
        id: int,
        title: str,
        caption: str,
        restrict: int,
        x_restrict: int,
        is_original: bool,
        image_urls: ImageUrls,
        create_date: datetime,
        tags: List[NovelTag],
        page_count: int,
        text_length: int,
        user: User,
        is_bookmarked: bool,
        total_bookmarks: int,
        total_view: int,
        visible: bool,
        total_comments: int,
        is_muted: bool,
        is_mypixiv_only: bool,
        is_x_restricted: bool,
        novel_ai_type: int,
        series: Optional[NovelSeries] = None,
    ) -> None:
        self.id = id
        self.title = title
        self.caption = caption
        self.restrict = restrict
        self.x_restrict = x_restrict
        self.is_original = is_original
        self.image_urls = image_urls
        self.create_date = create_date
        self.tags = tags
        self.page_count = page_count
        self.text_length = text_length
        self.user = user
        self.series = series
        self.is_bookmarked = is_bookmarked
        self.total_bookmarks = total_bookmarks
        self.total_view = total_view
        self.visible = visible
        self.total_comments = total_comments
        self.is_muted = is_muted
        self.is_mypixiv_only = is_mypixiv_only
        self.is_x_restricted = is_x_restricted
        self.novel_ai_type = novel_ai_type

        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["Novel"]:
        """See `PixivObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["image_urls"] = ImageUrls.de_json(data.pop("image_urls"), client)
        data["tags"] = NovelTag.de_list(data.pop("tags"), client)
        data["user"] = User.de_json(data.pop("user"), client)
        data["series"] = NovelSeries.de_json(data.pop("series"), client)

        return super().de_json(data=data, client=client)


class Novels(Page):
    """
    A model representing the response for a list of novels on Pixiv.

    Attributes:
        novels (List[Novel]): The novels by the user.
        next_url (Optional[str]): The next URL for pagination.

    Args:
        novels (List[Novel]): The novels by the user.
        next_url (Optional[str]): The next URL for pagination.
    """

    def __init__(
        self,
        novels: List[Novel],
        next_url: Optional[str] = None,
    ) -> None:
        super().__init__(next_url)

        self.novels = novels

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["Novels"]:
        """See `PixivObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["novels"] = Novel.de_list(data.pop("novels"), client)

        return super().de_json(data=data, client=client)


class NovelRecommended(Page):
    """
    A model for representing the response of the NovelRecommended API.

    Attributes:
        novels (List[Novel]): A list of recommended novel objects.
        ranking_novels (List[Novel]): A list of ranked novel objects.
        privacy_policy (Optional[PrivacyPolicy]): A privacy policy object associated with this work.
        next_url (str): The URL for the next page of recommended novels.

    Args:
        novels (List[Novel]): A list of recommended novel objects.
        ranking_novels (List[Novel]): A list of ranked novel objects.
        next_url (str): The URL for the next page of recommended novels.
        privacy_policy (Optional[PrivacyPolicy]): A privacy policy object associated with this work.
    """

    def __init__(
        self,
        novels: List[Novel],
        ranking_novels: List[Novel],
        next_url: Optional[str] = None,
        privacy_policy: Optional[PrivacyPolicy] = None,
    ) -> None:
        super().__init__(next_url)

        self.novels = novels
        self.ranking_novels = ranking_novels
        self.privacy_policy = privacy_policy

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["NovelRecommended"]:
        """See `PixivObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["novels"] = Novel.de_list(data.pop("novels"), client)
        data["ranking_novels"] = Novel.de_list(data.pop("ranking_novels"), client)
        data["privacy_policy"] = PrivacyPolicy.de_json(data.pop("privacy_policy"), client)

        return super().de_json(data=data, client=client)
