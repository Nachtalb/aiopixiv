import subprocess
from argparse import ArgumentParser, Namespace, _SubParsersAction
from base64 import urlsafe_b64encode
from getpass import getpass
from hashlib import sha256
from secrets import token_urlsafe
from typing import Any, Tuple

from playwright._impl._driver import compute_driver_executable, get_driver_env
from playwright.async_api import BrowserType, async_playwright
from yarl import URL

from aiopixiv._defaults import LOGIN_URL
from aiopixiv._utils.logging import get_logger

_LOGGER = get_logger(__name__)


def argparse(action: "_SubParsersAction[ArgumentParser]") -> None:
    parser = action.add_parser("auth", help="Help retrieving pixiv api credentials.")
    parser.add_argument("user", help="Pixiv Username or Mail")
    parser.add_argument("password", help="Pixiv Password", nargs="?")
    parser.set_defaults(func=login)


def s256(data: bytes) -> str:
    """S256 transformation method."""
    return urlsafe_b64encode(sha256(data).digest()).rstrip(b"=").decode("ascii")


def oauth_pkce(transform: Any) -> Tuple[str, str]:
    """Proof Key for Code Exchange by OAuth Public Clients (RFC7636)."""

    code_verifier = token_urlsafe(32)
    code_challenge = transform(code_verifier.encode("ascii"))

    return code_verifier, code_challenge


async def login(args: Namespace) -> bool:
    password = args.password or getpass()

    async with async_playwright() as pw:
        if not install(pw.chromium):
            _LOGGER.warning("Could not download and install chromium browser driver. Falling back to manual method.")
            _LOGGER.warning("Fallback (manual mode) not implemented yet.")
            return False
        browser = await pw.chromium.launch()

        code_verifier, code_challenge = oauth_pkce(s256)

        page = await browser.new_page()
        await page.goto(
            str(
                URL(LOGIN_URL).with_query(
                    {
                        "code_challenge": code_challenge,
                        "code_challenge_method": "S256",
                        "client": "pixiv-android",
                    }
                )
            )
        )
        __import__("ipdb").set_trace()
        return False


def install(browser: BrowserType) -> bool:
    driver_executable = str(compute_driver_executable())
    args = [driver_executable, "install", browser.name]

    _LOGGER.info("Installing chromium driver if not already installed.")
    process = subprocess.run(args, env=get_driver_env(), capture_output=True, text=True)
    return process.returncode == 0
