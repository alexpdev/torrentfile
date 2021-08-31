class BendecodingError(Exception):
    """Error occured during decode process."""

    def __init__(self, val, message=None):
        if not message:
            self.message = f"{type(val)} : {val} is of unknown value or type"
        else:
            self.message = message
        print(self.message)


class BenencodingError(Exception):
    """Error occured during encoding process."""

    def __init__(self, val, message=None):
        if not message:
            self.message = f"{type(val)} : {val} is of unknown value or type"
        else:
            self.message = message
        print(self.message)


class MissingArgError(Exception):
    def __init__(self, message="Missing Required Function Arguement"):
        self.message = message


class MissingTrackerError(MissingArgError):
    """*MissingTracker* Announce parameter is required.

    Subclass of builtin *Exception*.
    """

    def __init__(self, message=None):
        if message:
            self.message = message
        else:
            self.message = "Tracker arguement is missing and required"
        print(self.message)


class MissingPathError(MissingArgError):
    """*MissingPath* path parameter is required.

    Subclass of builtin *Exception*.
    """

    def __init__(self, message=None):
        """Path arguement is missing and required"""
        if message:
            self.message = message
        else:
            self.message = "Path arguement is missing and required"
        print(self.message)
