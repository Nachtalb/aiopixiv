import logging
from typing import Optional


def get_logger(file_name: str, class_name: Optional[str] = None) -> logging.Logger:
    """
    Returns a logger with an appropriated name.

    Examples:
        >>> logger = get_logger(__name__)
        >>> logger = get_logger(__name__, "MyClassName")

    Args:
        file_name (str): Name of the file the logger will be located at
        class_name (str, optional): Name of the class the logger will be used in
    """
    parts = file_name.split("_")
    if parts[1].startswith("utils") and class_name is None:
        name = parts[0].rstrip(".")
    else:
        name = f"{parts[0]}{class_name or parts[1].capitalize()}"
    return logging.getLogger(name)
