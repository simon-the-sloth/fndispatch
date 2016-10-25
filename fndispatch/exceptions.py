

class VersionError(Exception):
    pass


class VersionTooLow(VersionError):
    pass


class VersionTooHigh(VersionError):
    pass


class VersionNotFound(VersionError):
    pass