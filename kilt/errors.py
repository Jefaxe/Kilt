class AlreadyDownloaded(FileExistsError):
    pass


class EndOfSearch(IndexError):
    pass


class InvalidArgument(TypeError):
    pass
