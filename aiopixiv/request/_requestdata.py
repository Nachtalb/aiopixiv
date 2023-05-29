import json
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

from aiopixiv._utils.types import UploadFileDict
from aiopixiv.request._requestparameters import RequestParameter


class RequestData:
    """
    Instances of this class collect the data needed for one request to hte Pixiv API,
    including all parameters and files.

    Args:
        parameters (List[RequestParameter], optional): Parameters to be used in the request
    """

    __slots__ = ("_parameters", "containing_files")

    def __init__(self, parameters: Optional[List[RequestParameter]] = None) -> None:
        self._parameters = parameters or []
        self.containing_files: bool = any(param.input_files for param in self._parameters)

    @property
    def parameters(self) -> Dict[str, Union[str, int, List[Any], Dict[Any, Any]]]:
        """
        Gives the parameters as a mapping of name: value

        Value can be a single object of type int, float, str or bool or any (possibly
        nested) composition of lists, tuples and dictionaries, where each entry, key and
        value is of one of the mentioned types.
        """

        return {param.name: param.value for param in self._parameters if param.value is not None}  # type: ignore[misc]

    @property
    def json_parameters(self) -> Dict[str, str]:
        """
        Gives the parameters as a mapping of name: JSON encoded value
        """

        return {param.name: param.json_value for param in self._parameters if param.json_value is not None}

    def url_encoded_parameters(self, encode_kwargs: Optional[Dict[str, Any]] = None) -> str:
        """
        Encodes the parameters with urllib.parse.urlencode

        Args:
            encode_kwargs (Dict[str, Any], optional): Additional keyword arguments to pass along
                to urllib.parse.urlencode.
        """
        if encode_kwargs:
            return urlencode(self.json_parameters, **encode_kwargs)
        return urlencode(self.json_parameters)

    def parametrized_url(self, url: str, encode_kwargs: Optional[Dict[str, Any]] = None) -> str:
        """
        Shortcut for attaching the return value of url_encoded_parameters to the url.

        Args:
            url (str): The URL the parameters will be attached to.
            encode_kwargs (Dict[str, Any], optional): Additional keyword arguments ro pass along
                to urllib.parse.urlencode.
        """
        url_parameters = self.url_encoded_parameters(encode_kwargs=encode_kwargs)
        return f"{url}?{url_parameters}"

    @property
    def json_payload(self) -> bytes:
        """
        The parameters as UTF-8 encoded json payload
        """

        return json.dumps(self.json_parameters, ensure_ascii=False).encode("utf-8")

    async def multipart_data(self) -> UploadFileDict:
        """
        Gives the files contained in this object as mapping of part name to encoded content.
        """
        multipart_data: UploadFileDict = {}
        for param in self._parameters:
            m_data = await param.multipart_data()
            if m_data:
                multipart_data.update(m_data)
        return multipart_data
