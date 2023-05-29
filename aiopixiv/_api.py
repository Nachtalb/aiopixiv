import hashlib
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import AsyncContextManager, Mapping, Optional, TypeVar

from aiopath import AsyncPath
from yarl import URL

from aiopixiv._pixivobject import PixivObject
from aiopixiv._utils.logging import get_logger
from aiopixiv._utils.types import FilePath, JSONDict
from aiopixiv.error import AuthenticationError, NotAuthenticated, PixivError
from aiopixiv.models.authentication import AuthenticatedUser, Authentication
from aiopixiv.models.illust import Illust
from aiopixiv.request import HTTPXRequest, RequestData
from aiopixiv.request._requestparameters import RequestParameter

PA = TypeVar("PA", bound="PixivAPI")


class PixivAPI(PixivObject, AsyncContextManager["PixivAPI"]):
    """
    Base class for Pixiv API operations.

    Args:
        access_token (str, optional): Access token for authentication with Pixiv
        refresh_token (str, optional): Refresh token to re-authenticate with Pixiv after
            `access_token` expires.
        language (str, optional): Website language (i.e. "en-us", "zh-cn", ...), used
            among other things, for translated tags. (defaults to "en-us")
        api_host (str, optional): Host used for the API
        auth_host (str, optional): Host used for authentication
        client_id (str, optional): Client ID representing this API client (by default sourced from IOS app)
        client_secret (str, optional): Client Secret representing this API client (by default sourced from the IOS app)
        hash_secret (str, optional): Hash secret representing this API client (by default sourced from the IOS app)
    """

    _LOGGER = get_logger(__name__)

    __slots__ = (
        "_client_id",
        "_client_secret",
        "_hash_secret",
        "_api_host",
        "_auth_host",
        "_session",
        "_access_token",
        "_refresh_token",
        "_authenticated_user",
        "_initialized",
    )

    def __init__(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        language: Optional[str] = "en-us",
        api_host: str = "https://app-api.pixiv.net",
        auth_host: str = "https://oauth.secure.pixiv.net",
        client_id: str = "MOBrBDS8blbauoSck0ZfDbtuzpyT",
        client_secret: str = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj",
        hash_secret: str = "28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c",
    ) -> None:
        """
        Initialise the BasePixivAPI instance.

        Args:
            requests_kwargs (Any): Additional keyword arguments for the requests library.
        """
        self._access_token = access_token
        self._refresh_token = refresh_token

        self._api_host = api_host
        self._auth_host = auth_host
        self._client_id = client_id
        self._client_secret = client_secret
        self._hash_secret = hash_secret

        self._initialized = False

        self._authenticated_user: AuthenticatedUser

        headers = {
            "Referer": self._api_host,
        }
        if language:
            headers["Accept-Language"] = language

        self._session = HTTPXRequest(headers)

    def __repr__(self) -> str:
        if self._authenticated_user:
            return f'{self.__class__.__name__}(..., <authenticated="{self._authenticated_user.account}">)'
        return f"{self.__class__.__name__}()"

    def get_client(self) -> "PixivAPI":
        return self

    async def initialize(self) -> None:
        if self._initialized:
            self._LOGGER.debug("This API client is already initialised. Returning.")
            return

        await self._session.initialize()
        await self.authenticate()
        self._initialized = True

    async def shutdown(self) -> None:
        if not self._initialized:
            self._LOGGER.debug("This API client is already shut down. Returning.")
            return

        await self._session.shutdown()
        self._initialized = False

    async def __aenter__(self: PA) -> PA:
        try:
            await self.initialize()
            return self
        except Exception:
            await self.shutdown()
            raise

    async def __aexit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> None:
        await self.shutdown()

    async def get_authenticated_user(self) -> AuthenticatedUser:
        if self._authenticated_user:
            return self._authenticated_user
        elif self.is_authenticated:
            raise NotAuthenticated()
        else:
            await self.authenticate()

        return self._authenticated_user

    @property
    def is_authenticated(self) -> bool:
        """
        Check whether the user is authenticated.

        Warning:
            It determines this by checking wether the access credentials are set,
            it doesn't actually test whether they're valid. Use `PixivAPI.auth` for
            authentication.

        Returns:
            True if authenticated, else False
        """
        return bool(self._access_token and self._refresh_token)

    def _authentication_headers(self) -> dict[str, str]:
        """
        Build headers used for authentication
        """
        if not self._access_token:
            raise NotAuthenticated()

        headers = {
            "Authorization": f"Bearer {self._access_token}",
        }

        return headers

    async def authenticate(self, refresh_token: Optional[str] = None) -> None:
        if not refresh_token and not self._refresh_token:
            raise AttributeError(
                'Either "refresh_token" (auth argument) or "self._refresh_token" (during init) have to be set.'
            )

        localtime = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        headers = {
            "x-client-time": localtime,
            "x-client-hash": hashlib.md5(f"{localtime}{self._hash_secret}".encode()).hexdigest(),
        }

        data = {
            "get_secure_url": 1,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token or self._refresh_token,
        }

        try:
            response = await self._do_request(
                "auth/token",
                method="POST",
                params={},
                data=data,
                headers=headers,
                host=self._auth_host,
            )

            authentication = Authentication.de_json(response, self)
            if authentication is None:
                raise AuthenticationError("Could not authenticate with the given refresh token")
        except PixivError as exec:
            raise AuthenticationError("Could not authenticate with the given refresh token") from exec
        except (KeyError, TypeError, ValueError) as exec:
            raise AuthenticationError("Unsupported data returned from authentication endpoint") from exec

        self._access_token = authentication.access_token
        self._refresh_token = authentication.refresh_token
        self._authenticated_user = authentication.user

    async def _request(
        self,
        endpoint: str,
        method: str,
        params: Optional[JSONDict] = None,
        data: Optional[JSONDict] = None,
        needs_authentication: bool = False,
        *,
        api_kwargs: Optional[JSONDict],
    ) -> JSONDict:
        """
        Make a request to the PIXIV API

        Args:
            endpoint (str): Endpoint on the api host
            method (str): HTTP method (i.e. "GET", "POST", "PATCH", ...)
            params (JSONDict, optional): GET Parameters to send with the request
            data (JSONDict, optional): Data to send with the request
            needs_authentication (bool, optional): If true checks and sets authentication
                headers (defaults to False)
            **api_kwargs (optional): Arbitrary keyword arguments passed to the API.
                Can be used in case the API provides new features before they are
                implemented in aiopixiv.

        Returns:
            JSON parsed to a dict or a list of dicts
        """
        headers = {}
        if needs_authentication:
            headers = self._authentication_headers()

        if data is None:
            data = {}

        if params is None:
            params = {}

        if api_kwargs:
            data.update(api_kwargs)

        data = {key: value for key, value in data.items() if value is not None}
        params = {key: value for key, value in params.items() if value is not None}

        return await self._do_request(
            endpoint=endpoint,
            method=method,
            params=params,
            data=data,
            headers=headers,
        )

    async def _do_request(
        self,
        endpoint: str,
        method: str,
        params: JSONDict,
        data: JSONDict,
        headers: Optional[Mapping[str, str]] = None,
        host: Optional[str] = None,
    ) -> JSONDict:
        """
        Make a parsed request to Pixiv

        Args:
            endpoint (str): Endpoint on the api host
            method (str): HTTP method (i.e. "GET", "POST", "PATCH", ...)
            params (JSONDict, optional): Parameters to send with the request
            data (JSONDict, optional): Data to send with the request
            headers (Mapping[str, str], optional): Headers sent in addition to the default
                headers. Eg. for authentication.
            host (str, optional): Host to be requested (default to the api host defined
                during init)

        Returns:
            JSON parsed to a dict or a list of dicts
        """

        request_data = RequestData(parameters=[RequestParameter.from_input(key, value) for key, value in data.items()])
        request_params = RequestData(
            parameters=[RequestParameter.from_input(key, value) for key, value in params.items()]
        )
        return await self._session.parsed_request(
            url=f"{host or self._api_host}/{endpoint}",
            method=method,
            request_params=request_params,
            request_data=request_data,
            headers=headers or {},
        )

    async def _get(
        self,
        endpoint: str,
        params: Optional[JSONDict] = None,
        data: Optional[JSONDict] = None,
        needs_authentication: bool = False,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ) -> JSONDict:
        """
        Make a GET request to the PIXIV API

        Args:
            endpoint (str): Endpoint on the api host
            params (JSONDict, optional): GET Parameters to send with the request
            data (JSONDict, optional): Data to send with the request
            needs_authentication (bool, optional): If true checks and sets authentication
                headers (defaults to False)
            **api_kwargs (optional): Arbitrary keyword arguments passed to the API.
                Can be used in case the API provides new features before they are
                implemented in aiopixiv.

        Returns:
            JSON parsed to a dict or a list of dicts
        """
        return await self._request(
            endpoint=endpoint,
            method="GET",
            params=params,
            data=data,
            needs_authentication=needs_authentication,
            api_kwargs=api_kwargs,
        )

    async def _post(
        self,
        endpoint: str,
        data: Optional[JSONDict] = None,
        params: Optional[JSONDict] = None,
        *,
        needs_authentication: bool = False,
        api_kwargs: Optional[JSONDict] = None,
    ) -> JSONDict:
        """
        Make a POST request to the PIXIV API

        Args:
            endpoint (str): Endpoint on the api host
            data (JSONDict, optional): Data to send with the request
            params (JSONDict, optional): GET Parameters to send with the request
            needs_authentication (bool, optional): If true checks and sets authentication
                headers (defaults to False)
            **api_kwargs (optional): Arbitrary keyword arguments passed to the API.
                Can be used in case the API provides new features before they are
                implemented in aiopixiv.

        Returns:
            JSON parsed to a dict or a list of dicts
        """
        return await self._request(
            endpoint=endpoint,
            method="POST",
            params=params,
            data=data,
            needs_authentication=needs_authentication,
            api_kwargs=api_kwargs,
        )

    async def _patch(
        self,
        endpoint: str,
        data: Optional[JSONDict] = None,
        params: Optional[JSONDict] = None,
        *,
        needs_authentication: bool = False,
        api_kwargs: Optional[JSONDict] = None,
    ) -> JSONDict:
        """
        Make a PATCH request to the PIXIV API

        Args:
            endpoint (str): Endpoint on the api host
            data (JSONDict, optional): Data to send with the request
            params (JSONDict, optional): GET Parameters to send with the request
            needs_authentication (bool, optional): If true checks and sets authentication
                headers (defaults to False)
            **api_kwargs (optional): Arbitrary keyword arguments passed to the API.
                Can be used in case the API provides new features before they are
                implemented in aiopixiv.

        Returns:
            JSON parsed to a dict or a list of dicts
        """
        return await self._request(
            endpoint=endpoint,
            method="PATCH",
            params=params,
            data=data,
            needs_authentication=needs_authentication,
            api_kwargs=api_kwargs,
        )

    async def _delete(
        self,
        endpoint: str,
        data: Optional[JSONDict] = None,
        params: Optional[JSONDict] = None,
        *,
        needs_authentication: bool = False,
        api_kwargs: Optional[JSONDict] = None,
    ) -> JSONDict:
        """
        Make a DELETE request to the PIXIV API

        Args:
            endpoint (str): Endpoint on the api host
            data (JSONDict, optional): Data to send with the request
            params (JSONDict, optional): Parameters to send with the request
            needs_authentication (bool, optional): If true checks and sets authentication
                headers (defaults to False)
            **api_kwargs (optional): Arbitrary keyword arguments passed to the API.
                Can be used in case the API provides new features before they are
                implemented in aiopixiv.

        Returns:
            JSON parsed to a dict or a list of dicts
        """
        return await self._request(
            endpoint=endpoint,
            method="DELETE",
            data=data,
            params=params,
            needs_authentication=needs_authentication,
            api_kwargs=api_kwargs,
        )

    async def download(
        self,
        url: str,
        dir_path: Optional[FilePath] = None,
        file_name: Optional[str] = None,
        skip_existing: bool = False,
        needs_authentication: bool = True,
    ) -> AsyncPath:
        """
        Download a file from pixiv

        Args:
            url (str): The files URL
            dir_path (FilePath, optional): Path to directory to save file in (defaults to working dir)
            file_name (str, optional): Filename of the file (defaults to the filename in the URL)
            skip_existing (bool, optional): Skip already downloaded image (defaults to False)
            needs_authentication (bool, optional): If true checks and sets authentication
                headers (defaults to False)

        Returns:
            The final AsyncPath of the saved file.
        """
        dir_path = AsyncPath(Path(str(dir_path or "")).absolute())
        file_name = file_name or URL(url).name

        await dir_path.mkdir(parents=True, exist_ok=True)

        file_path = dir_path / file_name

        if skip_existing and await file_path.is_file():
            return file_path

        headers = {}
        if needs_authentication:
            headers = self._authentication_headers()

        async with self._session.retrieve(
            url=url,
            headers=headers,
        ) as content:
            async with file_path.open("wb") as file:
                async for data in content:
                    await file.write(data)

        return file_path

    async def illust(
        self,
        id: int,
        *,
        needs_authentication: bool = True,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Illust:
        params: JSONDict = {
            "illust_id": id,
        }

        result = await self._get(
            endpoint="v1/illust/detail",
            params=params,
            needs_authentication=needs_authentication,
            api_kwargs=api_kwargs,
        )

        return Illust.de_json(result["illust"], self)  # type: ignore[return-value]
