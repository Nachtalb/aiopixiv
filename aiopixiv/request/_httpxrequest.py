from contextlib import asynccontextmanager
from typing import AsyncIterator, Mapping, Optional, Tuple

import httpx

from aiopixiv._utils.logging import get_logger
from aiopixiv.error import NetworkError
from aiopixiv.request._baserequst import BaseRequest
from aiopixiv.request._requestdata import RequestData

_LOGGER = get_logger(__name__, "HTTPXRequest")


class HTTPXRequest(BaseRequest):
    """
    Implementation of BaseRequest using the library httpx <httpx://www.python-httpx.org>

    Args:
        default_headers (Mapping[str, str], optional): Default headers used for all requests.
            Should at least include a "Referer" to "https://pixiv.net" or similar, otherwise
            certain requests will return 403.
            To get translated tags you additionally need to set "Accept-Language" to a
            supported language such as "en-us" or "zh-cn".
    """

    __slots__ = ("_client", "_default_headers")

    def __init__(self, default_headers: Optional[Mapping[str, str]] = None) -> None:
        self._default_headers = httpx.Headers()

        self._default_headers.update({"User-Agent": self.USER_AGENT})
        self._default_headers.update(default_headers)

        self._client = self._build_client()

    def _build_client(self) -> httpx.AsyncClient:
        """
        Build and return a new client
        """
        return httpx.AsyncClient(headers=self._default_headers)

    async def initialize(self) -> None:
        """
        Initialize resources used by this class.
        """
        if not self._client.is_closed:
            _LOGGER.debug("This HTTPXRequest is already initialised. Returning.")
            return

        self._client = self._build_client()

    async def shutdown(self) -> None:
        """
        Stop & clear resources used by this class
        """
        if self._client.is_closed:
            _LOGGER.debug("This HTTPXRequest is already shut down. Returning.")
            return
        await self._client.aclose()

    async def do_request(
        self,
        url: str,
        method: str,
        request_params: Optional[RequestData] = None,
        request_data: Optional[RequestData] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Tuple[dict[str, str], int, bytes]:
        """
        Makes a request to the Pixiv API

        Args:
            url (str): The URL to request.
            method: (str): HTTP method (i.e. "GET", "POST", etc.).
            request_params (RequestData, optional): An object containing information about parameters
            request_data (RequestData, optional): An object containing information about body data
            headers (Mapping[str, str], optional): Headers sent in addition to the default
                headers. Eg. for authentication.

        Returns:
            A tuple of the http response header, code and the data as raw bytes.
        """

        if self._client.is_closed:
            raise RuntimeError("This Request is not initialized")

        files = await request_data.multipart_data() if request_data else None
        data = request_data.json_parameters if request_data else None
        params = request_params.json_parameters if request_params else None

        try:
            response = await self._client.request(
                method=method,
                url=url,
                data=data,
                params=params,
                files=files,
                headers=headers,
            )
        except httpx.HTTPError as err:
            raise NetworkError(f"httpx.{err.__class__.__name__}: {err}") from err

        return dict(response.headers), response.status_code, response.content

    @asynccontextmanager
    async def do_stream(
        self,
        url: str,
        method: str,
        request_params: Optional[RequestData] = None,
        request_data: Optional[RequestData] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> AsyncIterator[Tuple[dict[str, str], int, AsyncIterator[bytes]]]:
        """
        Makes a stream request to the Pixiv API

        Args:
            url (str): The URL to request.
            method: (str): HTTP method (i.e. "GET", "POST", etc.).
            request_params (RequestData, optional): An object containing information about parameters
            request_data (RequestData, optional): An object containing information about body data
            headers (Mapping[str, str], optional): Headers sent in addition to the default
                headers. Eg. for authentication.

        Returns:
            A tuple of the http response header, code and the content as an async iterator stream of bytes
        """

        if self._client.is_closed:
            raise RuntimeError("This Request is not initialized")

        files = await request_data.multipart_data() if request_data else None
        data = request_data.json_parameters if request_data else None
        params = request_params.json_parameters if request_params else None

        try:
            async with self._client.stream(
                method=method,
                url=url,
                data=data,
                params=params,
                files=files,
                headers=headers,
            ) as request:
                yield dict(request.headers), request.status_code, request.aiter_bytes()
        except httpx.HTTPError as err:
            raise NetworkError(f"httpx.{err.__class__.__name__}: {err}") from err
