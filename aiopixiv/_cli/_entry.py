import argparse
import asyncio
import sys

from aiopixiv._cli._auth import argparse as auth_argparse
from aiopixiv._cli._download import argparse as dl_argparse
from aiopixiv._defaults import VERSION

PARSERS = [auth_argparse, dl_argparse]
"""List of functions adding parsers to the cli for easy extensibility."""


async def main() -> int:
    """
    Main CLI entry point.

    Examples:
        # To extend the capability of this CLI, you can add another parser
        >>> from argparse import _SubParsersAction, ArgumentParser, Namespace
        >>> from aiopixiv._cli._entry import PARSERS

        >>> def my_foobar(args: Namespace) -> bool:
        >>>     print(f"Foo{'bar' if args.bar else ''}")

        >>> def my_argparser(action: _SubParsersAction[ArgumentParser]) -> None:
        >>>     # Create new parser
        >>>     parser = action.add_parser("foo", help="Foo all the way")
        >>>     # Add arguments
        >>>     parser.add_argument("--bar", help="Bar can't hurt either.", action="store_true")
        >>>     # Set your entry point
        >>>     parser.set_defaults(func=my_foobar)  # Define

        >>> # Add the parser to the CLI
        >>> PARSER.append(my_argparser)

    Returns:
        POSIX exit codes
    """
    parser = argparse.ArgumentParser(
        "aiopixiv",
        description=(
            "Aiopixiv is an efficient asyncio-based Python library, enabling seamless and concurrent interaction with"
            " the Pixiv API. Ideal for developing a wide range of applications from fanart crawlers to recommendation"
            " systems."
        ),
    )

    parser.add_argument("-V", "--version", action="store_true", help="Show version")
    subparsers = parser.add_subparsers()

    for sub_parser_adder in PARSERS:
        sub_parser_adder(subparsers)

    args = parser.parse_args()

    if args.version:
        print(f"aiopixiv: {VERSION}")
        return 1

    result = await args.func(args)
    if isinstance(result, int):
        return result
    return 0 if result else 1


def cli() -> None:
    sys.exit(asyncio.run(main()))
