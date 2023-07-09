import abc
import asyncio
import json
from contextlib import asynccontextmanager
from http import HTTPStatus
from types import TracebackType
from typing import AsyncContextManager, AsyncIterator, ClassVar, Mapping, Optional, Tuple, Type, TypeVar, Union

from httpx import Response

from aiopixiv._defaults import USER_AGENT as DEFAULT_USER_AGENT
from aiopixiv._utils.logging import get_logger
from aiopixiv._utils.types import JSONDict
from aiopixiv.error import APIError, APIErrorDetail, BadRequest, Forbidden, NetworkError, NotFound, PixivError
from aiopixiv.request._requestdata import RequestData

RT = TypeVar("RT", bound="BaseRequest")
T_Response = TypeVar("T_Response", bytes, Response)

_LOGGER = get_logger(__name__, "BaseRequest")


class BaseRequest(AsyncContextManager["BaseRequest"], abc.ABC):
    """
    Abstract interface class that allows aiopixiv to make requests to the Pixiv API.

    Can be implemented via different asyncio HTTP libraries such as httpx or aiohttp. An
    implementation of this class must implement all abstract methods and properties.

    Instances of this calass can be used as asyncio context managers.
    """

    USER_AGENT: ClassVar[str] = DEFAULT_USER_AGENT

    async def __aenter__(self: RT) -> RT:
        try:
            await self.initialize()
            return self
        except Exception as exc:
            await self.shutdown()
            raise exc

    async def __aexit__(
        self,
        __exc_type: Optional[Type[BaseException]],
        __exc_value: Optional[BaseException],
        __traceback: Optional[TracebackType],
    ) -> None:
        await self.shutdown()

    @abc.abstractmethod
    async def initialize(self) -> None:
        """
        Initialize resources used by this class.
        """

    @abc.abstractmethod
    async def shutdown(self) -> None:
        """
        Stop & clear resources used by this class
        """

    async def parsed_request(
        self,
        url: str,
        method: str,
        request_params: Optional[RequestData] = None,
        request_data: Optional[RequestData] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> JSONDict:
        """
        Makes a request to the Pixiv API, handles the return code and parses the answer.

        Args:
            url (str): The URL to request.
            method (str): HTTP method used (i.e. "POST", "GET", "DELETE", ...)
            request_params (RequestData, optional): An object containing information about parameters
            request_data (RequestData, optional): An object containing information about body data
            headers (Mapping[str, str], optional): Headers sent in addition to the default
                headers. Eg. for authentication.

        Returns:
            JSON parsed to a dict or a list of dicts
        """

        result = await self.request(
            url=url,
            method=method,
            request_params=request_params,
            request_data=request_data,
            headers=headers,
        )

        json_data = self.parse_json_payload(result)

        return json_data

    @asynccontextmanager
    async def retrieve(
        self,
        url: str,
        request_params: Optional[RequestData] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> AsyncIterator[AsyncIterator[bytes]]:
        """
        Retrieve a file by its URL as a stream

        Args:
            url (str): The web location we want to retrieve.
            request_params (RequestData, optional): An object containing information about parameters
            headers (Mapping[str, str], optional): Headers sent in addition to the default
                headers. Eg. for authentication.

        Returns:
            The content of the requested URL as async iterator stream returning bytes.
        """
        async with self.stream(
            url=url,
            method="GET",
            request_params=request_params,
            headers=headers,
        ) as content:
            yield content

    async def request(
        self,
        url: str,
        method: str,
        request_params: Optional[RequestData] = None,
        request_data: Optional[RequestData] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> bytes:
        """Wraps the real implementation request method.

        Performs the following tasks:
        * Handle the varions HTTP response codes.
        * Parse the Pixiv server response.

        Args:
            url (str): The URL to request.
            method (str): HTTP method (i.e. "POST", "GET", etc.).
            request_params (RequestData, optional): An object containing information about parameters
            request_data (RequestData, optional): An object containing information about body data
            headers (Mapping[str, str], optional): Headers sent in addition to the default
                headers. Eg. for authentication.

        Raises:
            Different kinds of PixivError depending on what went wrong.

        Returns:
            The content of the requested URL as raw bytes
        """
        try:
            _, code, payload = await self.do_request(
                url=url,
                method=method,
                request_params=request_params,
                request_data=request_data,
                headers=headers,
            )
        except asyncio.CancelledError as exc:
            raise exc
        except PixivError as exc:
            raise exc
        except Exception as exc:
            raise PixivError(f"Unknown error in HTTP request {repr(exc)}") from exc

        if HTTPStatus.OK <= code <= 299:
            return payload

        api_error, error = await self._parse_error(code, payload)
        if api_error:
            raise api_error from error
        raise error

    @asynccontextmanager
    async def stream(
        self,
        url: str,
        method: str,
        request_params: Optional[RequestData] = None,
        request_data: Optional[RequestData] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> AsyncIterator[AsyncIterator[bytes]]:
        """
        Wraps the real implementation stream request method.

        Performs the following tasks:
        * Handle the varions HTTP response codes.
        * Parse the Pixiv server response.
        * Starts a stream request (does not immediately parse the response content)

        Args:
            url (str): The URL to request.
            method (str): HTTP method (i.e. "POST", "GET", etc.).
            request_params (RequestData, optional): An object containing information about parameters
            request_data (RequestData, optional): An object containing information about body data
            headers (Mapping[str, str], optional): Headers sent in addition to the default
                headers. Eg. for authentication.

        Raises:
            API errors if possible otherwise more generic http errors. Either of them
            are desendants of PixivError.

        Returns:
            A context manager yielding an async iterator returning the response
            content as bytes.
        """
        try:
            async with self.do_stream(
                url=url,
                method=method,
                request_params=request_params,
                request_data=request_data,
                headers=headers,
            ) as (_, code, payload):
                if HTTPStatus.OK <= code <= 299:
                    yield payload
                    return

                api_error, error = await self._parse_error(code, payload)

        except asyncio.CancelledError:
            raise
        except PixivError:
            raise
        except Exception as exc:
            raise PixivError(f"Unknown error in HTTP request {repr(exc)}") from exc

        if api_error:
            raise api_error from error
        raise error

    async def _parse_error(
        self,
        code: int,
        content: Union[bytes, AsyncIterator[bytes]],
    ) -> Tuple[Optional[PixivError], PixivError]:
        """
        Parse returned error from a request

        Args:
            code (int): The HTTP status code
            content (Union[bytes, AsyncIterator[bytes]]): The content as returned by the `do_request` or `do_stream`.

        Returns:
            A tuple of if available an pixiv api error and a http error.
        """
        if isinstance(content, AsyncIterator):
            payload = b"".join([item async for item in content])
        else:
            payload = content

        api_error: Optional[PixivError] = None
        try:
            response_data = self.parse_json_payload(payload)["error"]
            message = response_data.get("message", "Unknown HTTPError")

            try:
                api_error = APIErrorDetail(**response_data)
            except TypeError:
                try:
                    api_error = APIError(**response_data)
                except TypeError:
                    pass
        except (json.JSONDecodeError, PixivError, KeyError):
            response_data = {}
            message = ""

        error: PixivError
        match code:
            case HTTPStatus.FORBIDDEN:
                error = Forbidden(message)
            case HTTPStatus.NOT_FOUND:
                error = NotFound(message)
            case HTTPStatus.BAD_REQUEST:
                __import__("ipdb").set_trace()
                error = BadRequest(message)
            case HTTPStatus.BAD_GATEWAY:
                error = NetworkError("Bad Gateway - Invalid response from server")
            case _:
                error = NetworkError(f"{message or 'NetworkError'} ({code})")

        return api_error, error

    @staticmethod
    def parse_json_payload(payload: bytes) -> JSONDict:
        """
        Parse the JSON returned from Pixiv.

        Args:
            payload (bytes): The UTF-8 encoded JSON payload as returned by Pixiv.

        Returns:
            dict: A JSON parsed as python dict with results.

        Raises:
            PixivError: If loading the JSON data failed.
        """
        decoded = payload.decode("utf-8", errors="replace")
        try:
            return json.loads(decoded)  # type: ignore[no-any-return]
        except ValueError as err:
            _LOGGER.error('Can not load invalid JSON data: "%s"', decoded)
            raise PixivError("Invalid server response") from err

    @abc.abstractmethod
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
            A tuple of the http response code and the data as raw bytes.
        """

    @abc.abstractmethod
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
        Context manager making a stream request to the Pixiv API

        Args:
            url (str): The URL to request.
            method: (str): HTTP method (i.e. "GET", "POST", etc.).
            request_params (RequestData, optional): An object containing information about parameters
            request_data (RequestData, optional): An object containing information about body data
            headers (Mapping[str, str], optional): Headers sent in addition to the default
                headers. Eg. for authentication.

        Returns:
            A tuple of the http response code and the content as an async iterator stream of bytes
        """
        yield  # type: ignore
