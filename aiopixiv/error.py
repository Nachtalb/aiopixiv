from typing import Any, Dict, List


class PixivError(Exception):
    """
    A model for representing generic errors.

    Attributes:
        message (str): The error message.

    Args:
        message (str): The error message.
    """

    __slots__ = ("message",)

    def __init__(self, message: str) -> None:
        super().__init__()

        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.message}')"


class APIErrorDetail(PixivError):
    """
    A model for representing an error message.

    Attributes:
        user_message (str): The user-friendly error message.
        message (str): The internal error message.
        reason (str): The reason for the error.
        user_message_details (dict): Additional details about the error message.

    Args:
        user_message (str): The user-friendly error message.
        message (str): The internal error message.
        reason (str): The reason for the error.
        user_message_details (dict): Additional details about the error message.
    """

    __slots__ = ("message", "user_message", "reason", "user_message_details")

    def __init__(
        self,
        user_message: str,
        message: str,
        reason: str,
        user_message_details: Dict[Any, Any],
    ) -> None:
        super().__init__(message)

        self.user_message = user_message
        self.reason = reason
        self.user_message_details = user_message_details


class APIError(PixivError):
    """
    A model for representing a generic api error.

    Attributes:
        error (bool): Indicates whether an error occurred.
        message (str): The error message.
        body (List): An empty list.

    Args:
        error (bool): Indicates whether an error occurred.
        message (str): The error message.
        body (List): An empty list.
    """

    __slots__ = ("error", "message", "body")

    def __init__(
        self,
        error: bool,
        message: str,
        body: List[Any],
    ) -> None:
        super().__init__(message)

        self.error = error
        self.body = body


class AuthenticationError(PixivError):
    """
    Raised during authentication process
    """

    __slots__ = ()


class NotAuthenticated(PixivError):
    """
    Raised when a authenticated request is done without authentication

    Args:
        message (str): Additional message for this error
    """

    __slots__ = ()

    def __init__(self, message: str = "You need to be authenticated for this request") -> None:
        super().__init__(message)


class NotFound(PixivError):
    """
    Raised when the API returns a not found error / 404
    """

    __slots__ = ()


class Forbidden(PixivError):
    """
    Raised when the API returns a permission error / 403
    """

    __slots__ = ()


class NetworkError(PixivError):
    """
    Base class for exceptions due to networking errors.
    """

    __slots__ = ()


class BadRequest(NetworkError):
    """
    Raised when Pixiv could not process the request correctly / 400.
    """

    __slots__ = ()
