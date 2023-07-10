from collections import defaultdict
from contextlib import asynccontextmanager
from io import BytesIO, FileIO
from itertools import cycle
from tempfile import NamedTemporaryFile, TemporaryDirectory, TemporaryFile
from typing import Any, AsyncIterator, Dict, Mapping, Optional, Sequence

import pytest
from aiopath import AsyncPath
from yarl import URL

from aiopixiv._api import PixivAPI
from aiopixiv._utils.types import JSONDict
from aiopixiv.error import AuthenticationError, NetworkError, NotAuthenticated
from aiopixiv.models.authentication import AuthenticatedUser
from aiopixiv.request import HTTPXRequest, RequestData
from tests.auxil.file import glob_dir
from tests.auxil.slots import mro_slots
from tests.data.assets import read_asset
from tests.data.urls import JOHN_WICK, JOHN_WICK_16x, url_asset_map


class TestPixivApiWithoutRequest:
    test_flag: Any = None

    @pytest.fixture(autouse=True)
    def _reset(self) -> None:
        self.test_flag = None

    async def test_slot_behaviour(self, pixiv_api: PixivAPI) -> None:
        for attr in pixiv_api.__slots__:
            assert getattr(pixiv_api, attr, "err") != "err", f"got extra slot '{attr}'"

        assert len(mro_slots(pixiv_api)) == len(set(mro_slots(pixiv_api))), "duplicate slot"

    async def test_to_dict(self, pixiv_api: PixivAPI) -> Any:
        to_dict_pixiv_api = pixiv_api.to_dict()

        assert isinstance(to_dict_pixiv_api, dict)
        assert to_dict_pixiv_api == {}

    async def test_initialize_and_shutdown(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async def initialize(*_: Any, **__: Any) -> None:
            self.test_flag = ["initialize"]

        async def stop(*_: Any, **__: Any) -> None:
            self.test_flag.append("stop")

        pixiv_api = PixivAPI()

        orig_stop = pixiv_api._session.shutdown

        try:
            monkeypatch.setattr(pixiv_api._session, "initialize", initialize)
            monkeypatch.setattr(pixiv_api._session, "shutdown", stop)
            await pixiv_api.initialize()
            assert self.test_flag == ["initialize"]

            await pixiv_api.shutdown()
            assert self.test_flag == ["initialize", "stop"]
        finally:
            await orig_stop()

    async def test_initialize_authenticates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async def authenticate(*_: Any, **__: Any) -> None:
            self.test_flag = "authenticate"

        pixiv_api = PixivAPI()

        monkeypatch.setattr(pixiv_api, "authenticate", authenticate)
        await pixiv_api.initialize()

        assert self.test_flag is None, "'authenticate' called even tho no tokens given"

        await pixiv_api.shutdown()

        pixiv_api._access_token = "aaa"
        pixiv_api._refresh_token = "bbb"
        await pixiv_api.initialize()
        assert self.test_flag == "authenticate"

    async def test_multiple_inits_and_shutdowns(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.test_flag = defaultdict(int)

        async def initialize(*_: Any, **__: Any) -> None:
            self.test_flag["init"] += 1

        async def shutdown(*_: Any, **__: Any) -> None:
            self.test_flag["shutdown"] += 1

        monkeypatch.setattr(HTTPXRequest, "initialize", initialize)
        monkeypatch.setattr(HTTPXRequest, "shutdown", shutdown)

        pixiv_api = PixivAPI()

        await pixiv_api.initialize()
        await pixiv_api.initialize()
        await pixiv_api.initialize()
        await pixiv_api.shutdown()
        await pixiv_api.shutdown()
        await pixiv_api.shutdown()

        assert self.test_flag["init"] == 1
        assert self.test_flag["shutdown"] == 1

    async def test_context_manager(self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch) -> None:
        async def initialize() -> None:
            self.test_flag = ["initialize"]

        async def shutdown(*_: Any) -> None:
            self.test_flag.append("stop")

        monkeypatch.setattr(pixiv_api, "initialize", initialize)
        monkeypatch.setattr(pixiv_api, "shutdown", shutdown)

        async with pixiv_api:
            pass

        assert self.test_flag == ["initialize", "stop"]

    async def test_context_manager_exception_on_init(
        self,
        pixiv_api: PixivAPI,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        async def initialize() -> None:
            raise RuntimeError("initialize")

        async def shutdown() -> None:
            self.test_flag = "stop"

        monkeypatch.setattr(pixiv_api, "initialize", initialize)
        monkeypatch.setattr(pixiv_api, "shutdown", shutdown)

        with pytest.raises(RuntimeError, match="initialize"):
            async with pixiv_api:
                pass

        assert self.test_flag == "stop"

    async def test_is_authenticated(self) -> None:
        pixiv_api_no_auth = PixivAPI()
        pixiv_api_with_auth = PixivAPI(access_token="aaaaa", refresh_token="bbbb")

        assert pixiv_api_no_auth.is_authenticated is False
        assert pixiv_api_with_auth.is_authenticated is True

    async def test_no_auth_exception_when_getting_auth_user(self) -> None:
        pixiv_api = PixivAPI()

        with pytest.raises(NotAuthenticated):
            await pixiv_api.get_authenticated_user()

    async def test_get_auth_user_with_authentication(self, pixiv_api: PixivAPI, auth_user: AuthenticatedUser) -> None:
        assert pixiv_api.is_authenticated is True
        assert await pixiv_api.get_authenticated_user() == auth_user

    async def test_try_to_auth_when_no_user_present_when_getting_auth_user(
        self,
        pixiv_api: PixivAPI,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        pixiv_api._authenticated_user = None

        self.test_flag = 0
        user_obj = object()

        async def authenticate() -> None:
            self.test_flag += 1
            pixiv_api._authenticated_user = user_obj  # type: ignore

        monkeypatch.setattr(pixiv_api, "authenticate", authenticate)

        user = await pixiv_api.get_authenticated_user()

        assert user is user_obj
        assert self.test_flag == 1

        await pixiv_api.get_authenticated_user()
        assert self.test_flag == 1, "Authentication should only be run once after the user has been set"

    async def test_authenticate_exception_on_bad_input_data(
        self,
        pixiv_api: PixivAPI,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        async def noop() -> Dict[Any, Any]:
            return {}

        monkeypatch.setattr(pixiv_api, "_do_request", noop)

        with pytest.raises(AttributeError):
            pixiv_api._refresh_token = None
            await pixiv_api.authenticate()

        with pytest.raises(AuthenticationError):
            # This is just to test that once we give it a refresh_token, everything is ok, but because we can't actually
            # log in during a test, we expect an authentication error given the patch of _do_request.
            await pixiv_api.authenticate(refresh_token="aaaaaaa")

        with pytest.raises(AuthenticationError):
            # Same as above but it shall use the refresh token set during init(), in case it's not given directly
            pixiv_api._refresh_token = "aaaaa"
            await pixiv_api.authenticate()

    async def test_authenticate_exception_on_bad_request_result(
        self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # No data to create authenticated user from
        async def bad_value_1(*_: Any, **__: Any) -> Dict[Any, Any]:
            return {}

        with pytest.raises(AuthenticationError, match="Could not authenticate"):
            monkeypatch.setattr(pixiv_api, "_do_request", bad_value_1)
            await pixiv_api.authenticate()

        # Not data compatible with authenticated user model
        async def bad_value_2(*_: Any, **__: Any) -> Dict[Any, Any]:
            return {"some_data": 123}

        with pytest.raises(AuthenticationError, match="Unsupported data"):
            monkeypatch.setattr(pixiv_api, "_do_request", bad_value_2)
            await pixiv_api.authenticate()

        # Unsupported response body
        async def bad_datatype(*_: Any, **__: Any) -> str:
            return ""

        with pytest.raises(AuthenticationError, match="Unsupported data"):
            monkeypatch.setattr(pixiv_api, "_do_request", bad_datatype)
            await pixiv_api.authenticate()

        # Error during communication with Pixiv
        async def error_during_networking(*_: Any, **__: Any) -> str:
            raise NetworkError("Test Fail")

        with pytest.raises(AuthenticationError, match="Could not authenticate"):
            monkeypatch.setattr(pixiv_api, "_do_request", error_during_networking)
            await pixiv_api.authenticate()

    async def test_auth_headers(self, pixiv_api: PixivAPI) -> None:
        correct_headers = {"Authorization": f"Bearer {pixiv_api._access_token}"}

        headers = pixiv_api._authentication_headers()
        assert headers == correct_headers

    async def test_auth_headers_set_in_request(self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch) -> None:
        async def _do_request(*_: Any, headers: Mapping[str, str], **__: Any) -> JSONDict:
            self.test_flag = headers
            return {}

        auth_headers = {"Authorization": f"Bearer {pixiv_api._access_token}"}

        monkeypatch.setattr(pixiv_api, "_do_request", _do_request)

        await pixiv_api._request(endpoint="/test", method="GET", api_kwargs={}, needs_authentication=False)
        assert self.test_flag == {}

        await pixiv_api._request(endpoint="/test", method="GET", api_kwargs={}, needs_authentication=True)
        assert self.test_flag == auth_headers

    async def test_api_kwargs_in_data_set_in_request(
        self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def _do_request(*_: Any, data: JSONDict, **__: Any) -> JSONDict:
            self.test_flag = data
            return {}

        monkeypatch.setattr(pixiv_api, "_do_request", _do_request)

        await pixiv_api._request(
            endpoint="/test",
            method="GET",
            data={"a": 1},
            api_kwargs={"b": 2},
            needs_authentication=False,
        )
        assert self.test_flag == {"a": 1, "b": 2}

    @pytest.mark.parametrize("http_method", ["get", "post", "patch", "delete"])
    async def test_request_alias(self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch, http_method: str) -> None:
        async def parsed_request(
            url: str,
            method: str,
            request_params: Optional[RequestData] = None,
            request_data: Optional[RequestData] = None,
            headers: Optional[Mapping[str, str]] = None,
        ) -> JSONDict:
            self.test_flag = {
                "url": url,
                "method": method,
                "request_params": request_params.json_parameters if request_params else None,
                "request_data": request_data.json_parameters if request_data else None,
                "headers": headers,
            }
            return {}

        monkeypatch.setattr(pixiv_api._session, "parsed_request", parsed_request)

        method = getattr(pixiv_api, "_" + http_method)

        await method(
            endpoint="/test",
            params={"a": 1},
            data={"b": 2},
            needs_authentication=False,
            api_kwargs={"c": 3},
        )

        assert self.test_flag == {
            "url": f"{pixiv_api._api_host}/test",
            "method": http_method.upper(),
            "request_params": {"a": "1"},
            "request_data": {"b": "2", "c": "3"},
            "headers": {},
        }

    async def _patch_retrieve(
        self,
        pixiv_api: PixivAPI,
        monkeypatch: pytest.MonkeyPatch,
        file_content: bytes | Sequence[bytes] = b"test",
    ) -> None:
        file_content_cycle = None
        if not isinstance(file_content, bytes):
            file_content_cycle = cycle(file_content)

        @asynccontextmanager
        async def retrieve(*_: Any, **__: Any) -> AsyncIterator[AsyncIterator[bytes]]:
            async def read() -> AsyncIterator[bytes]:
                if file_content_cycle:
                    yield next(file_content_cycle)
                else:
                    yield file_content  # type: ignore[misc]

            yield read()

        monkeypatch.setattr(pixiv_api._session, "retrieve", retrieve)

    async def test_download_file_with_dir(self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch) -> None:
        content = b"test content"
        await self._patch_retrieve(pixiv_api, monkeypatch, content)

        with TemporaryDirectory() as dir:
            sub_dir = AsyncPath(dir) / "sub_dir"
            assert await sub_dir.is_dir() is False

            await pixiv_api.download_to_file(JOHN_WICK, sub_dir)
            downloaded_file = AsyncPath(sub_dir) / URL(JOHN_WICK).name

            assert await sub_dir.is_dir() is True
            assert await glob_dir(sub_dir) == [downloaded_file]
            assert await downloaded_file.read_bytes() == content

    async def test_download_bytesio(self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch) -> None:
        content = b"test content"
        await self._patch_retrieve(pixiv_api, monkeypatch, content)

        result_1: BytesIO = await pixiv_api.download(url=JOHN_WICK)
        assert result_1.getvalue() == content

        pre_existing_bytesio = BytesIO()
        result_2: BytesIO = await pixiv_api.download(url=JOHN_WICK, file=pre_existing_bytesio)

        assert result_2.getvalue() == content
        assert pre_existing_bytesio.getvalue() == content
        assert id(result_2) == id(pre_existing_bytesio)

    async def test_download_with_open_file(self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch) -> None:
        content = b"test content"
        await self._patch_retrieve(pixiv_api, monkeypatch, content)

        with TemporaryFile(mode="b+w") as file:
            resulting_file: FileIO = await pixiv_api.download(url=JOHN_WICK, file=file)

            resulting_file.seek(0)
            assert resulting_file.read() == content
            file.seek(0)
            assert file.read() == content
            assert id(resulting_file) == id(file)

    async def test_download_many(self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch) -> None:
        contents = [b"aaaaaaaaaaaaaa", b"bbbbbbbbbbbbbb"]
        await self._patch_retrieve(pixiv_api=pixiv_api, monkeypatch=monkeypatch, file_content=contents)

        received_contents_1: list[bytes] = []
        async for item in pixiv_api.download_many(urls=[JOHN_WICK, JOHN_WICK]):
            received_contents_1.append(item.getvalue())

        assert sorted(received_contents_1) == contents

        received_contents_2: list[BytesIO] = []
        containers = [BytesIO(), BytesIO()]
        async for item in pixiv_api.download_many(urls=[JOHN_WICK, JOHN_WICK_16x], files=containers):
            received_contents_2.append(item)

        received_contents_2.sort(key=lambda f: f.getvalue())

        # We can't make sure to get the correct order as download_many uses "as_completed" so the cycled `contents`
        # could be in any order
        assert containers[0].getvalue() in contents
        assert containers[1].getvalue() in contents
        assert containers[0].getvalue() != containers[1].getvalue()
        assert id(received_contents_2[0]) == id(containers[0])
        assert id(received_contents_2[1]) == id(containers[1])

    async def test_download_many_to_files_single_dir_no_filenames(
        self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        contents = [b"aaaaaaaaaaaaaa", b"bbbbbbbbbbbbbb"]
        await self._patch_retrieve(pixiv_api=pixiv_api, monkeypatch=monkeypatch, file_content=contents)

        with TemporaryDirectory() as dir:
            temp_dir = AsyncPath(dir)
            urls = [JOHN_WICK, JOHN_WICK_16x]
            correct_paths = [temp_dir / URL(url).name for url in urls]

            received_paths = []
            async for item in pixiv_api.download_many_to_file(urls=urls, dir_paths=dir):
                received_paths.append(item)

            assert sorted(received_paths) == correct_paths
            assert all([await path.is_file() for path in received_paths])
            assert sorted([await path.read_bytes() for path in received_paths]) == contents

    async def test_download_many_to_files_single_dir_multi_filename(
        self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        contents = [b"aaaaaaaaaaaaaa", b"bbbbbbbbbbbbbb"]
        await self._patch_retrieve(pixiv_api=pixiv_api, monkeypatch=monkeypatch, file_content=contents)

        with TemporaryDirectory() as dir:
            temp_dir = AsyncPath(dir)
            urls = [JOHN_WICK, JOHN_WICK_16x]
            filenames = ["aaaaa.jpeg", "bbbbb.jpeg"]
            correct_paths = [temp_dir / filename for filename in filenames]

            received_paths = []
            async for item in pixiv_api.download_many_to_file(urls=urls, dir_paths=dir, file_names=filenames):
                received_paths.append(item)

            assert sorted(received_paths) == correct_paths
            assert all([await path.is_file() for path in received_paths])
            assert sorted([await path.read_bytes() for path in received_paths]) == contents

    async def test_download_many_to_files_multi_dir_multi_filenames(
        self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        contents = [b"aaaaaaaaaaaaaa", b"bbbbbbbbbbbbbb"]
        await self._patch_retrieve(pixiv_api=pixiv_api, monkeypatch=monkeypatch, file_content=contents)

        with TemporaryDirectory() as dir:
            temp_dir = AsyncPath(dir)
            urls = [JOHN_WICK, JOHN_WICK_16x]
            sub_dirs = [temp_dir / "aaaa", temp_dir / "bbbb"]
            filenames = ["aaaaa.jpeg", "bbbbb.jpeg"]
            correct_paths = [sub_dir / filename for sub_dir, filename in zip(sub_dirs, filenames)]

            received_paths = []
            async for item in pixiv_api.download_many_to_file(urls=urls, dir_paths=sub_dirs, file_names=filenames):
                received_paths.append(item)

            assert sorted(received_paths) == correct_paths
            assert all([await path.is_file() for path in received_paths])
            assert sorted([await path.read_bytes() for path in received_paths]) == contents

    async def test_download_many_to_files_multi_dir_no_filesnames(
        self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        contents = [b"aaaaaaaaaaaaaa", b"bbbbbbbbbbbbbb"]
        await self._patch_retrieve(pixiv_api=pixiv_api, monkeypatch=monkeypatch, file_content=contents)

        with TemporaryDirectory() as dir:
            temp_dir = AsyncPath(dir)
            urls = [JOHN_WICK, JOHN_WICK_16x]
            sub_dirs = [temp_dir / "aaaa", temp_dir / "bbbb"]
            correct_paths = [sub_dir / URL(url).name for sub_dir, url in zip(sub_dirs, urls)]

            received_paths = []
            async for item in pixiv_api.download_many_to_file(urls=urls, dir_paths=sub_dirs):
                received_paths.append(item)

            assert sorted(received_paths) == correct_paths
            assert all([await path.is_file() for path in received_paths])
            assert sorted([await path.read_bytes() for path in received_paths]) == contents

    async def test_download_many_to_files_multi_dir_single_filesnames(
        self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        contents = [b"aaaaaaaaaaaaaa", b"bbbbbbbbbbbbbb"]
        await self._patch_retrieve(pixiv_api=pixiv_api, monkeypatch=monkeypatch, file_content=contents)

        with TemporaryDirectory() as dir:
            temp_dir = AsyncPath(dir)
            urls = [JOHN_WICK, JOHN_WICK_16x]
            sub_dirs = [temp_dir / "aaaa", temp_dir / "bbbb"]
            filename = "a_file.jpeg"
            correct_paths = [sub_dir / filename for sub_dir in sub_dirs]

            received_paths = []
            async for item in pixiv_api.download_many_to_file(urls=urls, dir_paths=sub_dirs, file_names=filename):
                received_paths.append(item)

            assert sorted(received_paths) == correct_paths
            assert all([await path.is_file() for path in received_paths])
            assert sorted([await path.read_bytes() for path in received_paths]) == contents

    async def test_download_file_with_dir_and_filename(
        self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        content = b"test content"
        await self._patch_retrieve(pixiv_api, monkeypatch, content)

        with NamedTemporaryFile() as file:
            file = AsyncPath(file.name)
            assert await file.read_bytes() == b""

            await pixiv_api.download_to_file(JOHN_WICK, file.parent, file.name)

            assert await file.is_file() is True
            assert await file.read_bytes() == content

    async def test_download_skip_existing(self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch) -> None:
        content = b"test content"
        await self._patch_retrieve(pixiv_api, monkeypatch, content)

        with NamedTemporaryFile() as file:
            file = AsyncPath(file.name)
            assert await file.read_bytes() == b""

            await pixiv_api.download_to_file(JOHN_WICK, file.parent, file.name, skip_existing=True)

            assert await file.is_file() is True
            assert await file.read_bytes() == b"", "File should not have been overwritten"


class TestPixivApiWithRequest:
    test_flag: Any = None

    async def test_download_file(self, pixiv_api: PixivAPI, monkeypatch: pytest.MonkeyPatch) -> None:
        with NamedTemporaryFile() as file:
            file = AsyncPath(file.name)
            assert await file.read_bytes() == b""

            await pixiv_api.download_to_file(JOHN_WICK_16x, file.parent, file.name)

            assert await file.is_file() is True
            assert await file.read_bytes() == await read_asset(url_asset_map[JOHN_WICK_16x])
