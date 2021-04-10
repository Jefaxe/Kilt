
class AlreadyDownloaded(FileExistsError):
    pass


class EndOfSearch(IndexError):
    pass


class InvalidArgument(TypeError):
    pass


class VersionNotFound(Exception):
    pass


class NoVersionFound(VersionNotFound):
    pass


class SpecificVersionNotFound(VersionNotFound):
    pass


class InvalidModId(Exception):
    pass
