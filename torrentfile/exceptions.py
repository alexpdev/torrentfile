class BendecodingError(Exception):
    """Error occured during decode process."""

    def __init__(self, val):
        message = f"{type(val)} : {val} is of unknown value or type"
        super().__init__(message)


class BenencodingError(Exception):
    """Error occured during encoding process."""

    def __init__(self, val):
        message = f"{type(val)} : {val} is of unknown value or type"
        super().__init__(message)


class MissingArgError(Exception):
    def __init__(self, message=None):
        if not message:
            message = "Missing Required Function Arguement"
        super().__init__(message)


class MissingTrackerError(MissingArgError):
    """Announce parameter is required.""" ""

    def __init__(self, message=None):
        if not message:
            self.message = "Tracker arguement is missing and required"
        super().__init__(message)


class MissingPathError(MissingArgError):
    """Path parameter is required."""

    def __init__(self, message=None):
        """Path arguement is missing and required"""
        if not message:
            self.message = "Path arguement is missing and required"
        super().__init__(message)


class PieceLengthError(Exception):
    def __init__(self, val, message=None):
        if not message:
            message = f"{val} is not a power of 2"
        super().__init__(message)
