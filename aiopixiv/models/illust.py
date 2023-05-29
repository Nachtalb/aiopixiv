from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from aiopixiv._pixivobject import PixivObject
from aiopixiv._utils.types import JSONDict
from aiopixiv.models.novel import Novel
from aiopixiv.models.page import Page
from aiopixiv.models.tag import Tag
from aiopixiv.models.urls import ImageUrls, MetaPagesUrls, MetaSinglePageUrl
from aiopixiv.models.user import User

if TYPE_CHECKING:
    from aiopixiv._api import PixivAPI


class Illust(PixivObject):
    """
    This model represents an image illustration on Pixiv.

    Attributes:
        id (int): The illustration's ID.
        title (str): The illustration's title.
        type (str): The illustration's type.
        image_urls (ImageUrls): URLs of the illustration's images.
        caption (str): The illustration's caption.
        restrict (int): The illustration's restrict level.
        user (User): The user who created the illustration.
        tags (List[Tag]): The illustration's tags.
        tools (List[str]): The tools used to create the illustration.
        create_date (datetime): The illustration's creation date.
        page_count (int): The number of pages in the illustration.
        width (int): The illustration's width.
        height (int): The illustration's height.
        sanity_level (int): The illustration's sanity level.
        x_restrict (int): The illustration's x_restrict level.
        series (Optional[str]): The illustration's series.
        meta_single_page (MetaSinglePage): Meta information for single-page illustrations.
        meta_pages (List[MetaPage]): Meta information for multi-page illustrations.
        total_view (int): The illustration's total view count.
        total_bookmarks (int): The illustration's total bookmark count.
        is_bookmarked (bool): Whether the illustration is bookmarked.
        visible (bool): Whether the illustration is visible.
        is_muted (bool): Whether the illustration is muted.
        total_comments (int): The illustration's total comment count.
        illust_ai_type (int): The illustration's AI type.
        illust_book_style (int): The illustration's book style.
        comment_access_control (int): Access control level to comments

    Args:
        id (int): The illustration's ID.
        title (str): The illustration's title.
        type (str): The illustration's type.
        image_urls (ImageUrls): URLs of the illustration's images.
        caption (str): The illustration's caption.
        restrict (int): The illustration's restrict level.
        user (User): The user who created the illustration.
        tags (List[Tag]): The illustration's tags.
        tools (List[str]): The tools used to create the illustration.
        create_date (datetime): The illustration's creation date.
        page_count (int): The number of pages in the illustration.
        width (int): The illustration's width.
        height (int): The illustration's height.
        sanity_level (int): The illustration's sanity level.
        x_restrict (int): The illustration's x_restrict level.
        series (Optional[str]): The illustration's series.
        meta_single_page (MetaSinglePage): Meta information for single-page illustrations.
        meta_pages (List[MetaPage]): Meta information for multi-page illustrations.
        total_view (int): The illustration's total view count.
        total_bookmarks (int): The illustration's total bookmark count.
        is_bookmarked (bool): Whether the illustration is bookmarked.
        visible (bool): Whether the illustration is visible.
        is_muted (bool): Whether the illustration is muted.
        total_comments (int): The illustration's total comment count.
        illust_ai_type (int): The illustration's AI type.
        illust_book_style (int): The illustration's book style.
        comment_access_control (int): Access control level to comments
    """

    def __init__(
        self,
        id: int,
        title: str,
        type: str,
        image_urls: ImageUrls,
        caption: str,
        restrict: int,
        user: User,
        tags: List[Tag],
        tools: List[str],
        create_date: datetime,
        page_count: int,
        width: int,
        height: int,
        sanity_level: int,
        x_restrict: int,
        meta_single_page: MetaSinglePageUrl,
        meta_pages: List[MetaPagesUrls],
        total_view: int,
        total_bookmarks: int,
        is_bookmarked: bool,
        visible: bool,
        is_muted: bool,
        total_comments: int,
        illust_ai_type: int,
        illust_book_style: int,
        comment_access_control: int,
        series: Optional[str] = None,
    ) -> None:
        super().__init__()

        self.id = id
        self.title = title
        self.type = type
        self.image_urls = image_urls
        self.caption = caption
        self.restrict = restrict
        self.user = user
        self.tags = tags
        self.tools = tools
        self.create_date = create_date
        self.page_count = page_count
        self.width = width
        self.height = height
        self.sanity_level = sanity_level
        self.x_restrict = x_restrict
        self.series = series
        self.meta_single_page = meta_single_page
        self.meta_pages = meta_pages
        self.total_view = total_view
        self.total_bookmarks = total_bookmarks
        self.is_bookmarked = is_bookmarked
        self.visible = visible
        self.is_muted = is_muted
        self.total_comments = total_comments
        self.illust_ai_type = illust_ai_type
        self.illust_book_style = illust_book_style
        self.comment_access_control = comment_access_control

        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["Illust"]:
        """See `PixivObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["image_urls"] = ImageUrls.de_json(data.pop("image_urls"), client)
        data["user"] = User.de_json(data.pop("user"), client)
        data["tags"] = Tag.de_list(data.pop("tags"), client)
        data["meta_single_page"] = MetaSinglePageUrl.de_json(data.pop("meta_single_page"), client)
        data["meta_pages"] = MetaPagesUrls.de_json(data.pop("meta_pages"), client)

        return super().de_json(data=data, client=client)


class Illusts(Page):
    """
    A subclass of Page representing a page of illustrations.

    Attributes:
        illusts: (List[Illust]): A list of illustrations
        next_url (Optional[str]): The next URL for pagination

    Args:
        illusts: (List[Illust]): A list of illustrations
        next_url (Optional[str]): The next URL for pagination
    """

    def __init__(
        self,
        illusts: List[Illust],
        next_url: Optional[str] = None,
    ) -> None:
        super().__init__(next_url)

        self.illusts = illusts

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["Illusts"]:
        """See `PixivObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["illusts"] = Illust.de_list(data.pop("illusts"), client)

        return super().de_json(data=data, client=client)


class UserPreview(Page):
    """
    A model representing the response for a user's preview illustrations and novels on Pixiv.

    Attributes:
        user (User): The user's basic information.
        illusts (List[Illust]): The illustrations by the user.
        next_url (Optional[str]): The next URL for pagination.
        is_muted (bool): Whether the user is muted.
    """

    def __init__(
        self,
        is_muted: bool,
        illusts: List[Illust],
        novels: List[Novel],
        next_url: Optional[str] = None,
    ) -> None:
        super().__init__(next_url)

        self.is_muted = is_muted
        self.illusts = illusts
        self.novels = novels

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["UserPreview"]:
        """See `PixivObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["illusts"] = Illust.de_list(data.pop("illusts"), client)
        data["novels"] = Novel.de_list(data.pop("novels"), client)

        return super().de_json(data=data, client=client)
