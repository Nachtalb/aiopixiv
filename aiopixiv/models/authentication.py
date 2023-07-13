from typing import TYPE_CHECKING, Optional

from aiopixiv._pixivobject import PixivObject
from aiopixiv._utils.types import JSONDict

if TYPE_CHECKING:
    from aiopixiv._api import PixivAPI


class AuthenticatedUserImageUrls(PixivObject):
    """
    A model representing the user image URLs of the authenticated user.

    Attributes:
        px_16x16 (str): URL of the small sized profile image.
        px_50x50 (str): URL of the medium sized profile image.
        px_170x170 (str): URL of the big sized profile image.

    Args:
        px_16x16 (str): URL of the small sized profile image.
        px_50x50 (str): URL of the medium sized profile image.
        px_170x170 (str): URL of the big sized profile image.
    """

    def __init__(
        self,
        px_16x16: str,
        px_50x50: str,
        px_170x170: str,
    ) -> None:
        super().__init__()

        self.px_16x16 = px_16x16
        self.px_50x50 = px_50x50
        self.px_170x170 = px_170x170

        self._id_attrs = (self.px_16x16,)


class AuthenticatedUser(PixivObject):
    """
    A model representing the authenticated user's basic information.

    Attributes:
        id (str): The user's ID.
        name (str): The user's display name.
        account (str): The user's username.
        profile_image_urls (AuthenticatedUserImageUrls): URLs of the user's profile images.
        mail_address (str): The users configured email address.
        is_mail_authorized (bool): Whether the email of the user has been validated.
        is_premium (bool): Whether the user bought the premium subscription.
        x_restrict (int): Up to which level of restriction content is shown (2 = R18)

    Args:
        id (int): The user's ID.
        name (str): The user's display name.
        account (str): The user's username.
        profile_image_urls (AuthenticatedUserImageUrls): URLs of the user's profile images.
        mail_address (str): The users configured email address.
        is_mail_authorized (bool): Whether the email of the user has been validated.
        is_premium (bool): Whether the user bought the premium subscription.
        x_restrict (int): Up to which level of restriction content is shown (2 = R18)
    """

    def __init__(
        self,
        id: int,
        name: str,
        account: str,
        profile_image_urls: AuthenticatedUserImageUrls,
        mail_address: str,
        is_mail_authorized: bool,
        is_premium: bool,
        x_restrict: int,
    ) -> None:
        super().__init__()

        self.id = id
        self.name = name
        self.account = account
        self.profile_image_urls = profile_image_urls
        self.mail_address = mail_address
        self.is_mail_authorized = is_mail_authorized
        self.is_premium = is_premium
        self.x_restrict = x_restrict

        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["AuthenticatedUser"]:
        """See `PixivObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["profile_image_urls"] = AuthenticatedUserImageUrls.de_json(data.pop("profile_image_urls"), client)

        return super().de_json(data=data, client=client)


class Authentication(PixivObject):
    """
    A model representing the response during authentication.

    Attributes:
        access_token (str): Pixiv API access token
        refresh_token (str): Pixiv API refresh token
        expires_in (int): Time until token expires in seconds
        user (User): Authenticated user
        token_type (str): The type of the token
        scope (str): The permission scope

    Args:
        access_token (str): Pixiv API access token
        refresh_token (str): Pixiv API refresh token
        expires_in (int): Time until token expires in seconds
        user (User): Authenticated user
        token_type (str): The type of the token
        scope (str): The permission scope
    """

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        expires_in: int,
        user: AuthenticatedUser,
        token_type: str,
        scope: str,
    ) -> None:
        super().__init__()

        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.user = user
        self.token_type = token_type
        self.scope = scope

        self._id_attrs = (self.access_token,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["Authentication"]:
        data = cls._parse_data(data)

        if not data:
            return None

        data.pop("response")

        data["user"] = AuthenticatedUser.de_json(data.pop("user"), client)

        return super().de_json(data, client)
