from typing import Optional

from aiopixiv._pixivobject import PixivObject


class ImageUrls(PixivObject):
    """
    This object represents Pixiv image urls.

    On Pixiv there are images with multiple preprocessed versions of it available.
    These are represented with this class.

    Attributes:
        square_medium (str): URL of the square medium-sized image.
        medium (str): URL of the medium-sized image.
        large (str): URL of the large-sized image.
        original (Optional[str]): URL of the original-sized image.

    Args:
        square_medium (str): URL of the square medium-sized image.
        medium (str): URL of the medium-sized image.
        large (str): URL of the large-sized image.
        original (Optional[str]): URL of the original-sized image.
    """

    def __init__(
        self,
        square_medium: str,
        medium: str,
        large: str,
        original: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.square_medium = square_medium
        self.medium = medium
        self.large = large
        self.original = original

        self._id_attrs = (self.original,)


class MetaSinglePageUrl(PixivObject):
    """
    This model represents meta information about a single page illustration.

    Attributes:
        original_image_url (Optional[str]): URL of the original-sized image.

    Args:
        original_image_url (Optional[str]): URL of the original-sized image.
    """

    def __init__(
        self,
        original_image_url: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.original_image_url = original_image_url

        self._id_attrs = (self.original_image_url,)


class MetaPagesUrls(PixivObject):
    """
    This models represents the meta information about a multi page illustration.

    Attributes:
        image_urls (ImageUrls): URLs of the images for this page.

    Args:
        image_urls (ImageUrls): URLs of the images for this page.
    """

    def __init__(self, image_urls: ImageUrls) -> None:
        super().__init__()

        self.image_urls = image_urls

        self._id_attrs = (self.image_urls,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], client: "PixivAPI") -> Optional["MetaPagesUrls"]:
        """See `PixivObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["image_urls"] = ImageUrls.de_json(data.pop("image_urls"), client)

        return super().de_json(data=data, client=client)
