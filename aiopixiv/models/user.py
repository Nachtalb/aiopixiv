from typing import TYPE_CHECKING, List, Optional

from aiopixiv._pixivobject import PixivObject
from aiopixiv._utils.types import JSONDict
from aiopixiv.models.page import Page

if TYPE_CHECKING:
    from aiopixiv._api import PixivAPI


class ProfileImageUrls(PixivObject):
    """
    A model representing the profile image URLs of a Pixiv user.

    Attributes:
        medium (str): URL of the medium sized profile image.

    Args:
        medium (str): URL of the medium sized profile image.
    """

    def __init__(
        self,
        medium: str,
    ) -> None:
        super().__init__()

        self.medium = medium

        self._id_attrs = (self.medium,)


class User(PixivObject):
    """
    A model representing a Pixiv user's basic information.

    Attributes:
        id (str): The user's ID.
        name (str): The user's display name.
        account (str): The user's username.
        profile_image_urls (ProfileImageUrls): URLs of the user's profile images.
        comment (str): The user's comment or description.
        is_followed (bool): Whether the user is followed.
        is_access_blocking_user (bool): Whether the user is access blocking.

    Args:
        id (int): The user's ID.
        name (str): The user's display name.
        account (str): The user's username.
        profile_image_urls (ProfileImageUrls): URLs of the user's profile images.
        comment (str): The user's comment or description.
        is_followed (bool): Whether the user is followed.
        is_access_blocking_user (bool, optional): Whether the user is access blocking.
    """

    def __init__(
        self,
        id: int,
        name: str,
        account: str,
        profile_image_urls: ProfileImageUrls,
        is_followed: bool,
        is_access_blocking_user: Optional[bool] = None,
        comment: Optional[str] = None,
    ) -> None:
        super().__init__()

        self.id = id
        self.name = name
        self.account = account
        self.profile_image_urls = profile_image_urls
        self.comment = comment
        self.is_followed = is_followed
        self.is_access_blocking_user = is_access_blocking_user

        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["User"]:
        """See `PixivObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["profile_image_urls"] = ProfileImageUrls.de_json(data.pop("profile_image_urls"), client)

        return super().de_json(data=data, client=client)


class Users(Page):
    """
    A model representing the response for a list of users on Pixiv.

    Attributes:
        users (List[User]): The users by the user.
        next_url (Optional[str]): The next URL for pagination.

    Args:
        users (List[User]): The users by the user.
        next_url (Optional[str]): The next URL for pagination.
    """

    def __init__(
        self,
        users: List[User],
        next_url: Optional[str] = None,
    ) -> None:
        super().__init__(next_url)

        self.users = users

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["Users"]:
        """See `PixivObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["user"] = User.de_json(data.pop("user"), client)

        return super().de_json(data=data, client=client)


class Profile(PixivObject):
    """
    A model representing a Pixiv user's profile information.

    Attributes:
        webpage (Optional[str]): The user's webpage URL.
        gender (str): The user's gender.
        birth (str): The user's birth date.
        birth_day (str): The user's birth day.
        birth_year (int): The user's birth year.
        region (str): The user's region.
        address_id (int): The user's address ID.
        country_code (str): The user's country code.
        job (str): The user's job.
        job_id (int): The user's job ID.
        total_follow_users (int): The total number of users followed by the user.
        total_mypixiv_users (int): The total number of mypixiv users of the user.
        total_illusts (int): The total number of illustrations by the user.
        total_manga (int): The total number of manga by the user.
        total_novels (int): The total number of novels by the user.
        total_illust_bookmarks_public (int): The total number of public illust bookmarks of the user.
        total_illust_series (int): The total number of illust series by the user.
        total_novel_series (int): The total number of novel series by the user.
        background_image_url (Optional[str]): The URL of the user's background image.
        twitter_account (str): The user's Twitter account.
        twitter_url (str): The user's Twitter URL.
        pawoo_url (str): The user's Pawoo URL.
        is_premium (bool): Whether the user has a premium account.
        is_using_custom_profile_image (bool): Whether the user is using a custom profile image.

    Args:
        webpage (Optional[str]): The user's webpage URL.
        gender (str): The user's gender.
        birth (str): The user's birth date.
        birth_day (str): The user's birth day.
        birth_year (int): The user's birth year.
        region (str): The user's region.
        address_id (int): The user's address ID.
        country_code (str): The user's country code.
        job (str): The user's job.
        job_id (int): The user's job ID.
        total_follow_users (int): The total number of users followed by the user.
        total_mypixiv_users (int): The total number of mypixiv users of the user.
        total_illusts (int): The total number of illustrations by the user.
        total_manga (int): The total number of manga by the user.
        total_novels (int): The total number of novels by the user.
        total_illust_bookmarks_public (int): The total number of public illust bookmarks of the user.
        total_illust_series (int): The total number of illust series by the user.
        total_novel_series (int): The total number of novel series by the user.
        background_image_url (Optional[str]): The URL of the user's background image.
        twitter_account (str): The user's Twitter account.
        twitter_url (str): The user's Twitter URL.
        pawoo_url (str): The user's Pawoo URL.
        is_premium (bool): Whether the user has a premium account.
        is_using_custom_profile_image (bool): Whether the user is using a custom profile image.
    """

    def __init__(
        self,
        gender: str,
        birth: str,
        birth_day: str,
        birth_year: int,
        region: str,
        address_id: int,
        country_code: str,
        job: str,
        job_id: int,
        total_follow_users: int,
        total_mypixiv_users: int,
        total_illusts: int,
        total_manga: int,
        total_novels: int,
        total_illust_bookmarks_public: int,
        total_illust_series: int,
        total_novel_series: int,
        background_image_url: str,
        twitter_account: str,
        twitter_url: str,
        pawoo_url: str,
        is_premium: bool,
        is_using_custom_profile_image: bool,
        webpage: Optional[str] = None,
    ) -> None:
        self.webpage = webpage
        self.gender = gender
        self.birth = birth
        self.birth_day = birth_day
        self.birth_year = birth_year
        self.region = region
        self.address_id = address_id
        self.country_code = country_code
        self.job = job
        self.job_id = job_id
        self.total_follow_users = total_follow_users
        self.total_mypixiv_users = total_mypixiv_users
        self.total_illusts = total_illusts
        self.total_manga = total_manga
        self.total_novels = total_novels
        self.total_illust_bookmarks_public = total_illust_bookmarks_public
        self.total_illust_series = total_illust_series
        self.total_novel_series = total_novel_series
        self.background_image_url = background_image_url
        self.twitter_account = twitter_account
        self.twitter_url = twitter_url
        self.pawoo_url = pawoo_url
        self.is_premium = is_premium
        self.is_using_custom_profile_image = is_using_custom_profile_image


class ProfilePublicity(PixivObject):
    """
    A model representing a Pixiv user's profile publicity settings.

    Attributes:
        gender (str): The user's gender publicity setting.
        region (str): The user's region publicity setting.
        birth_day (str): The user's birth day publicity setting.
        birth_year (str): The user's birth year publicity setting.
        job (str): The user's job publicity setting.
        pawoo (bool): Whether the user's Pawoo is public.

    Args:
        gender (str): The user's gender publicity setting.
        region (str): The user's region publicity setting.
        birth_day (str): The user's birth day publicity setting.
        birth_year (str): The user's birth year publicity setting.
        job (str): The user's job publicity setting.
        pawoo (bool): Whether the user's Pawoo is public.
    """

    def __init__(
        self,
        gender: str,
        region: str,
        birth_day: str,
        birth_year: str,
        job: str,
        pawoo: bool,
    ) -> None:
        super().__init__()

        self.gender = gender
        self.region = region
        self.birth_day = birth_day
        self.birth_year = birth_year
        self.job = job
        self.pawoo = pawoo


class Workspace(PixivObject):
    """
    A model representing a Pixiv user's workspace information.

    Attributes:
        pc (str): The user's PC information.
        monitor (str): The user's monitor information.
        tool (str): The user's tool information.
        scanner (str): The user's scanner information.
        tablet (str): The user's tablet information.
        mouse (str): The user's mouse information.
        printer (str): The user's printer information.
        desktop (str): The user's desktop information.
        music (str): The user's music information.
        desk (str): The user's desk information.
        chair (str): The user's chair information.
        comment (str): The user's workspace comment.
        workspace_image_url (Optional[str]): The URL of the user's workspace image.

    Args:
        pc (str): The user's PC information.
        monitor (str): The user's monitor information.
        tool (str): The user's tool information.
        scanner (str): The user's scanner information.
        tablet (str): The user's tablet information.
        mouse (str): The user's mouse information.
        printer (str): The user's printer information.
        desktop (str): The user's desktop information.
        music (str): The user's music information.
        desk (str): The user's desk information.
        chair (str): The user's chair information.
        comment (str): The user's workspace comment.
        workspace_image_url (Optional[str]): The URL of the user's workspace image.
    """

    def __init__(
        self,
        pc: str,
        monitor: str,
        tool: str,
        scanner: str,
        tablet: str,
        mouse: str,
        printer: str,
        desktop: str,
        music: str,
        desk: str,
        chair: str,
        comment: str,
        workspace_image_url: Optional[str] = None,
    ) -> None:
        super().__init__()

        self.pc = pc
        self.monitor = monitor
        self.tool = tool
        self.scanner = scanner
        self.tablet = tablet
        self.mouse = mouse
        self.printer = printer
        self.desktop = desktop
        self.music = music
        self.desk = desk
        self.chair = chair
        self.comment = comment
        self.workspace_image_url = workspace_image_url


class UserDetail(PixivObject):
    """
    A model representing a Pixiv user's detailed information.

    Attributes:
        user (User): The user's basic information.
        profile (Profile): The user's profile information.
        profile_publicity (ProfilePublicity): The user's profile publicity settings.
        workspace (Workspace): The user's workspace information.

    Args:
        user (User): The user's basic information.
        profile (Profile): The user's profile information.
        profile_publicity (ProfilePublicity): The user's profile publicity settings.
        workspace (Workspace): The user's workspace information.
    """

    def __init__(
        self,
        user: User,
        profile: Profile,
        profile_publicity: ProfilePublicity,
        workspace: Workspace,
    ) -> None:
        super().__init__()

        self.user = user
        self.profile = profile
        self.profile_publicity = profile_publicity
        self.workspace = workspace

        self._id_attrs = (self.user.id,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["UserDetail"]:
        """See `PixivObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["user"] = User.de_json(data.pop("user"), client)
        data["profile"] = Profile.de_json(data.pop("profile"), client)
        data["profile_publicity"] = ProfilePublicity.de_json(data.pop("profile_publicity"), client)
        data["workspace"] = Workspace.de_json(data.pop("workspace"), client)

        return super().de_json(data=data, client=client)
