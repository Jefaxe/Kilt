import semantic_version

__version__ = semantic_version.Version("0.1.0-beta.7")


def get_site():
    return "https://api.modrinth.com/api/v1/mod"


def get_query():
    return get_site() + "?query={}&limit={}&index={}&offset={}"


def get_kilt_doc():
    return "https://github.com/Jefaxe/Kilt/wiki"


def get_labrinth_doc():
    return "https://github.com/modrinth/labrinth/wiki/API-Documentation"
