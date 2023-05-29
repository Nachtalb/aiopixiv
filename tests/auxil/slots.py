import inspect


def mro_slots(obj: object, only_parents: bool = False) -> list[str]:
    """Returns a list of all slots of a class and its parents.
    Args:
        obj (:obj:`type`): The class or class-instance to get the slots from.
        only_parents (:obj:`bool`, optional): If ``True``, only the slots of the parents are
            returned. Defaults to ``False``.
    """
    cls = obj if inspect.isclass(obj) else obj.__class__

    classes = cls.__mro__[1:] if only_parents else cls.__mro__

    return [
        attr
        for cls in classes
        if hasattr(cls, "__slots__")  # The Exception class doesn't have slots
        for attr in cls.__slots__  # pyright: ignore[reportGeneralTypeIssues]
    ]
