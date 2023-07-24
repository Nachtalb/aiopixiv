import pytest

from aiopixiv._api import PixivAPI
from aiopixiv.models.authentication import AuthenticatedUser, AuthenticatedUserImageUrls
from tests.data import urls as data_urls


@pytest.fixture
async def pixiv_api(auth_user: AuthenticatedUser) -> PixivAPI:
    api = PixivAPI(
        access_token="aaaaaaa",
        refresh_token="bbbbbbb",
    )
    api._authenticated_user = auth_user
    api._initialized = True
    return api


@pytest.fixture
async def auth_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        id=0,
        account="john_wick",
        is_mail_authorized=True,
        is_premium=True,
        mail_address="john@wick.kills",
        name="John Wick",
        x_restrict=2,
        profile_image_urls=AuthenticatedUserImageUrls(
            px_16x16=data_urls.JOHN_WICK_16x,
            px_50x50=data_urls.JOHN_WICK_50x,
            px_170x170=data_urls.JOHN_WICK_170x,
        ),
    )
