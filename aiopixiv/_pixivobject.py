import json
from datetime import datetime
from itertools import chain
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Set, Sized, Tuple, Type, TypeVar, Union
from warnings import warn

from aiopixiv._utils.datetime import to_timestamp
from aiopixiv._utils.types import JSONDict

if TYPE_CHECKING:
    from aiopixiv._api import PixivAPI


T_PixivObject = TypeVar("T_PixivObject", bound="PixivObject")


class PixivObject:
    """
    The base objects for all api types
    """

    __slots__ = ("_id_attrs", "_client")

    def __init__(self) -> None:
        self._id_attrs: Tuple[object, ...] = ()

    def __repr__(self) -> str:
        """
        Gives a string representation of this object in the form of
        ``ClassName(attr_1=value_1, attr2_=value_2, ...)``, where attributes are omitted
        if they have the value None or are empty instances of Sized (e.g. list, dict,
        set, str, etc.).

        As this class doesn't implement __str__, the default implementation will be used,
        which is equivalent to __repr__.

        Returns:
            str
        """

        as_dict = self._get_attrs(recursive=False, include_private=False)

        contents = ", ".join(
            f"{key}={as_dict[key]!r}"
            for key in sorted(as_dict.keys())
            if (
                as_dict[key] is not None
                and not (isinstance(as_dict[key], Sized) and len(as_dict[key]) == 0)  # type: ignore[arg-type]
            )
        )

        return f"{self.__class__.__name__}({contents})"

    def __getitem__(self, item: str) -> object:
        """
        Objects of this type are subscriptable with strings, where
        ``pixiv_object["attribute_name"]`` is equivalent to ``pixiv_object.attribute_name``.

        Tip:
            This is useful for dynamic attribute lookup, i.e. ``pixiv_object[arg]`` where
            the value of ``arg`` is determined at runtime.
            In all other cases, it's recommended to use the dot notation instead.

        Args:
            item (str): The name of the attribute to look up.

        Returns:
            object

        Raises:
            KeyError: If the object does not have an attribute with the appropriate name.
        """
        try:
            return getattr(self, item)
        except AttributeError as exec:
            raise KeyError(
                f"Objects of type {self.__class__.__name__} don't have an attribute called `{item}`."
            ) from exec

    @staticmethod
    def _parse_data(data: Optional[JSONDict]) -> Optional[JSONDict]:
        """
        Should be called by subclasses that override de_json to ensure that the input is
        not altered. Whoever calls de_json might still want to use the original input for
        something else.
        """
        return None if data is None else data.copy()

    @classmethod
    def de_json(
        cls: Type[T_PixivObject],
        data: Optional[JSONDict],
        client: "PixivAPI",
    ) -> Optional[T_PixivObject]:
        """
        Converts JSON data to a Pixiv object.

        Args:
            data (Dict[str, Any]): The JSON data.
            client (PixivAPI): The client associated with this object.

        Return:
            The Pixiv object
        """
        return cls._de_json(data=data, client=client)

    @classmethod
    def _de_json(
        cls: Type[T_PixivObject],
        data: Optional[JSONDict],
        client: "PixivAPI",
    ) -> Optional[T_PixivObject]:
        if data is None:
            return None

        obj = cls(**data)
        obj.set_client(client=client)
        return obj

    @classmethod
    def de_list(
        cls: Type[T_PixivObject],
        data: Optional[List[JSONDict]],
        client: "PixivAPI",
    ) -> Tuple[T_PixivObject, ...]:
        """
        Converts a list of JSON objects to a tuple of Pixiv objects.

        Args:
            data (List[Dict[str, Any]]): The JSON data.
            client (PixivAPI): The client associated with these objects.

        Returns:
            A tuple of Pixiv objects.
        """
        if not data:
            return ()

        return tuple(obj for obj in (cls.de_json(d, client) for d in data) if obj is not None)

    def to_json(self) -> str:
        """
        Gives a JSON representation of the object.

        Returns:
            The object as JSON.
        """
        return json.dumps(self.to_dict())

    def to_dict(self, recursive: bool = True) -> JSONDict:
        """
        Gives a dict representation of the object.

        Args:
            recursive (bool, optional): If True, will convert any PixivObject (if found)
                in the attributes to a dictionary. Else preserves it as an object itself.
                Defaults to true.

        Returns:
            The object as a dict.
        """
        out = self._get_attrs(recursive=recursive)

        pop_keys: Set[str] = set()
        for key, value in out.items():
            if isinstance(value, (tuple, list)):
                if not value:
                    pop_keys.add(key)
                    continue

                val = []
                for item in value:
                    if hasattr(item, "to_dict"):
                        val.append(item.to_dict(recursive=recursive))
                    elif isinstance(item, (tuple, list)):
                        val.append([i.to_dict(recursive=recursive) if hasattr(i, "to_dict") else i for i in item])
                    else:
                        val.append(item)
                out[key] = val
            elif isinstance(value, datetime):
                out[key] = to_timestamp(value)

        for key in pop_keys:
            out.pop(key)

        return out

    def _get_attrs(
        self,
        include_private: bool = False,
        recursive: bool = False,
        remove_client: bool = False,
    ) -> Dict[str, Union[str, object]]:
        """
        This method is used for obtaining the attributes of the object.

        Args:
            include_private (bool): Whether the result should include private variables.
            recursive (bool): If True, will convert any "PixivObjects" (if found) in
                attributes to a dictionary. Else, preserves it as an object itself.
            remove_client (bool): Whether the client should be included in the result.

        Returns:
            Dict: A dict where the keys are attributes names and values are their values.
        """
        data = {}
        for key in self._get_attrs_names(include_private=include_private):
            value = getattr(self, key, None)
            if value is not None:
                if recursive and hasattr(value, "to_dict"):
                    data[key] = value.to_dict(recursive=True)
                else:
                    data[key] = value
            elif not recursive:
                data[key] = value

        if remove_client:
            data.pop("_client", None)
        return data

    def _get_attrs_names(self, include_private: bool) -> Iterator[str]:
        """
        Return the names of the attributes of this object. This is used to determine which
        attributes should be serialised.

        Args:
            include_private (bool): Whether to include private attributes.

        Returns:
            Iterator[str]: An iterator over the names of the attributes of this object.
        """
        all_slots = (s for c in self.__class__.__mro__[:-1] for s in c.__slots__)  # type: ignore
        all_attrs = chain(all_slots, self.__dict__.keys()) if hasattr(self, "__dict__") else all_slots
        if include_private:
            return all_attrs
        return (attr for attr in all_attrs if not attr.startswith("_"))

    def get_client(self) -> "PixivAPI":
        """
        Retruns the "PixivAPI" instance associated with this object.

        Raises:
            RuntimeError: If no "PixivAPI" instance was set for this object.
        """
        if self._client is None:
            raise RuntimeError("This object has no bot associated with it.")
        return self._client

    def set_client(self, client: "PixivAPI") -> None:
        """
        Set the "PixivAPI" instance associated with this object.


        Args:
            client (PixivAPI): The associated client
        """
        self._client = client

    def __eq__(self, other: object) -> bool:
        """
        Compares this object with other in terms of equality.

        If this object and other are not objects of the same class, this comparison will
        fall back to Python's default implementation. Otherwise, are equal, if the
        corresponding subclass of "PixivObject" has defined a set of attributes to compare
        and all these attributes are equal. If the subclass has not defined a set of
        attributes to compare, a warning will be issued.

        Args:
            other (object): The object to compare with.

        Returns:
            bool
        """
        if isinstance(other, self.__class__):
            if not self._id_attrs:
                warn(
                    f"Objects of type {self.__class__.__name__} can not be meaningfully tested for equivalence.",
                    stacklevel=2,
                )
            if not other._id_attrs:
                warn(
                    f"Objects of type {other.__class__.__name__} can not be meaningfully tested for equivalence.",
                    stacklevel=2,
                )

            return self._id_attrs == other._id_attrs
        return super().__eq__(other)

    def __hash__(self) -> int:
        """
        Builds a hash value for this object such that the hash of two objects is equal if
        and only if the objects are equal in terms of __eq__

        Returns:
            int
        """
        if self._id_attrs:
            return hash((self.__class__, self._id_attrs))
        return super().__hash__()
