from datetime import datetime
from typing import List, Optional

from aiopixiv.models.illust import Illust
from aiopixiv.models.tag import Tag
from aiopixiv.models.urls import ImageUrls, MetaPagesUrls, MetaSinglePageUrl
from aiopixiv.models.user import User


class MangaIllust(Illust):
    """
    A subclass of Illust representing an illustration on Pixiv with type 'manga'.

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
    """

    def __init__(
        self,
        id: int,
        title: str,
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
        type: str = "manga",
        series: Optional[str] = None,
    ) -> None:
        super().__init__(
            id=id,
            title=title,
            type=type,
            image_urls=image_urls,
            caption=caption,
            restrict=restrict,
            user=user,
            tags=tags,
            tools=tools,
            create_date=create_date,
            page_count=page_count,
            width=width,
            height=height,
            sanity_level=sanity_level,
            x_restrict=x_restrict,
            series=series,
            meta_single_page=meta_single_page,
            meta_pages=meta_pages,
            total_view=total_view,
            total_bookmarks=total_bookmarks,
            is_bookmarked=is_bookmarked,
            visible=visible,
            is_muted=is_muted,
            total_comments=total_comments,
            illust_ai_type=illust_ai_type,
            illust_book_style=illust_book_style,
        )
