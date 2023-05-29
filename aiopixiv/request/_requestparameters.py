import json
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Sequence, Tuple

from aiopixiv._pixivobject import PixivObject
from aiopixiv._utils.datetime import to_timestamp
from aiopixiv._utils.types import UploadFileDict
from aiopixiv.request._inputfile import InputFile


@dataclass(repr=True, eq=False, order=False, frozen=True)
class RequestParameter:
    """Instances of this class represent a single parameter to be sent along with a request to
    the Pixiv API.

    Args:
        name (str): The name of the parameter.
        value (object, optional): The value of the parameter. Must be JSON-serialisable.
        input_files (List[telegram.InputFile], optional): A list of files that should be
            uploaded along with this parameter.

    Attributes:
        name (str): The name of the parameter.
        value (object, optional): The value of the parameter.
        input_files (List[InputFile | None): A list of files that should be uploaded along
            with this parameter.
    """

    __slots__ = ("name", "value", "input_files")

    name: str
    value: object
    input_files: Optional[List[InputFile]]

    @property
    def json_value(self) -> Optional[str]:
        """
        The JSON serialised value or None if value is None.
        """
        if isinstance(self.value, str):
            return self.value
        if self.value is None:
            return None
        return json.dumps(self.value)

    async def multipart_data(self) -> Optional[UploadFileDict]:
        """
        A dict with the file data to upload, if any.
        """
        if not self.input_files:
            return None
        return {self.name: await input_file.field_tuple() for input_file in self.input_files}

    @staticmethod
    def _value_and_input_files_from_input(  # pylint: disable=too-many-return-statements
        value: object,
    ) -> Tuple[object, List[InputFile]]:
        """
        Converts `value` into something that we can json-dump.

        Returns:
            A tuple of the json serialisable value and a list of InputFiles.
        """
        match value:
            case datetime():
                return to_timestamp(value), []
            case InputFile():
                return None, [value]
            case PixivObject():
                return value.to_dict(), []
            case _:
                return value, []

    @classmethod
    def from_input(cls, key: str, value: object) -> "RequestParameter":
        """
        Builds an instance of this class for a given key-value pair that represents the raw
        input as passed along from the api client instance.
        """
        if not isinstance(value, (str, bytes)) and isinstance(value, Sequence):
            param_values = []
            input_files = []
            for obj in value:
                param_value, input_file = cls._value_and_input_files_from_input(obj)
                if param_value is not None:
                    param_values.append(param_value)
                input_files.extend(input_file)
            return RequestParameter(name=key, value=param_values, input_files=input_files if input_files else None)

        param_value, input_files = cls._value_and_input_files_from_input(value)
        return RequestParameter(name=key, value=param_value, input_files=input_files if input_files else None)
