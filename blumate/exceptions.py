"""Exceptions used by Home Assistant."""


class BluMateError(Exception):
    """General Home Assistant exception occurred."""

    pass


class InvalidEntityFormatError(BluMateError):
    """When an invalid formatted entity is encountered."""

    pass


class NoEntitySpecifiedError(BluMateError):
    """When no entity is specified."""

    pass


class TemplateError(BluMateError):
    """Error during template rendering."""

    def __init__(self, exception):
        """Initalize the error."""
        super().__init__('{}: {}'.format(exception.__class__.__name__,
                                         exception))
