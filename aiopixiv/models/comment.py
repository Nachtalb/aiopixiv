from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from aiopixiv._pixivobject import PixivObject
from aiopixiv._utils.types import JSONDict
from aiopixiv.models.page import Page
from aiopixiv.models.user import User

if TYPE_CHECKING:
    from aiopixiv._api import PixivAPI


class Comment(PixivObject):
    """
    A Comment model for representing comment data on an illustration.

    Attributes:
        id (int): The comment's unique identifier.
        comment (str): The comment text.
        date (datetime): The date the comment was made.
        user (User): The user who made the comment.
        parent_comment (Optional[dict]): The parent comment if this is a reply to another comment.

    Args:
        id (int): The comment's unique identifier.
        comment (str): The comment text.
        date (datetime): The date the comment was made.
        user (User): The user who made the comment.
        parent_comment (Optional[dict]): The parent comment if this is a reply to another comment.
    """

    def __init__(
        self,
        id: int,
        comment: str,
        date: datetime,
        user: User,
        parent_comment: Optional["Comment"] = None,
    ) -> None:
        super().__init__()

        self.id = id
        self.comment = comment
        self.date = date
        self.user = user
        self.parent_comment = parent_comment

        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["Comment"]:
        data = cls._parse_data(data)

        if not data:
            return None

        data["user"] = User.de_json(data.pop("user"), client)
        data["parent_comment"] = Comment.de_json(data.pop("parent_comment"), client)

        return super().de_json(data, client)


class Comments(Page):
    """
    A model for representing the response of the Comments API.

    Attributes:
        total_comments (int): The total number of comments on the illustration.
        comments (List[Comment]): A list of comment objects.
        next_url (Optional[str]): The URL for the next page of comments, if available.
        comment_access_control (int): The comment access control level.

    Args:
        total_comments (int): The total number of comments on the illustration.
        comments (List[Comment]): A list of comment objects.
        next_url (Optional[str]): The URL for the next page of comments, if available.
        comment_access_control (int): The comment access control level.
    """

    def __init__(
        self,
        total_comments: int,
        comments: List["Comment"],
        comment_access_control: int,
        next_url: Optional[str] = None,
    ) -> None:
        super().__init__(next_url)

        self.total_comments = total_comments
        self.comments = comments
        self.comment_access_control = comment_access_control

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["Comments"]:
        data = cls._parse_data(data)

        if not data:
            return None

        data["comments"] = Comment.de_list(data.pop("parent_comment"), client)

        return super().de_json(data, client)
