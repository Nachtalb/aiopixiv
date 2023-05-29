from aiopixiv._pixivobject import PixivObject


class PrivacyPolicy(PixivObject):
    """
    A PrivacyPolicy model for representing privacy notices from pixiv.net

    Attributes:
        version (str): Version of the policy eg: `2-en`
        message (str): A message about policy
        url (str): URL to the policy text

    Args:
        version (str): Version of the policy eg: `2-en`
        message (str): A message about policy
        url (str): URL to the policy text
    """

    def __init__(
        self,
        version: str,
        message: str,
        url: str,
    ) -> None:
        super().__init__()

        self.version = version
        self.message = message
        self.url = url
