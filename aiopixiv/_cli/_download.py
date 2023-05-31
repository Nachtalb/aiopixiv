from argparse import ArgumentParser, Namespace, _SubParsersAction


def argparse(action: "_SubParsersAction[ArgumentParser]") -> None:
    parser = action.add_parser("download", help="Download illustrations, mangas and novels from Pixiv.", aliases=["dl"])
    parser.add_argument("-i", "--illust", help="ID or URL of the illustration.", nargs="?")
    parser.add_argument("-m", "--manga", help="ID or URL of the manga", nargs="?")
    parser.add_argument("-n", "--novel", help="ID or URL of the novel", nargs="?")
    parser.set_defaults(func=download)


async def download(args: Namespace) -> bool:
    print("This functionality has not been implemented yet")
    return False
