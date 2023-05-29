from collections import defaultdict
from typing import Any

import pytest

from aiopixiv._api import PixivAPI
from aiopixiv.request import HTTPXRequest
from tests.auxil.slots import mro_slots


class TestPixivApiWithoutRequest:
    test_flag: Any = None

    @pytest.fixture(autouse=True)
    def _reset(self) -> None:
        self.test_flag = None

    async def test_slot_behaviour(self) -> None:
        pixiv_api = PixivAPI()
        for attr in pixiv_api.__slots__:
            assert getattr(pixiv_api, attr, "err") != "err", f"got extra slot '{attr}'"

        assert len(mro_slots(pixiv_api)) == len(set(mro_slots(pixiv_api))), "duplicate slot"

    async def test_to_dict(self) -> Any:
        pixiv_api = PixivAPI()
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

    async def test_context_manager(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async def initialize() -> None:
            self.test_flag = ["initialize"]

        async def shutdown(*_: Any) -> None:
            self.test_flag.append("stop")

        pixiv_api = PixivAPI()

        monkeypatch.setattr(pixiv_api, "initialize", initialize)
        monkeypatch.setattr(pixiv_api, "shutdown", shutdown)

        async with pixiv_api:
            pass

        assert self.test_flag == ["initialize", "stop"]

    async def test_context_manager_exception_on_init(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async def initialize() -> None:
            raise RuntimeError("initialize")

        async def shutdown() -> None:
            self.test_flag = "stop"

        pixiv_api = PixivAPI()

        monkeypatch.setattr(pixiv_api, "initialize", initialize)
        monkeypatch.setattr(pixiv_api, "shutdown", shutdown)

        with pytest.raises(RuntimeError, match="initialize"):
            async with pixiv_api:
                pass

        assert self.test_flag == "stop"
