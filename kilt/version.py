import semantic_version
import datetime

__version__ = semantic_version.Version("0.1.0-beta.7+build.2021.04.18")
__name__ = "Kilt"
_feature = "Initial release; modrinth support"
_patch = None
_commit = "Back to Beta!"
_changelog = """
        Added version metadata
        Remembered i need to implement facets for 0.1 :("""

prerelease_dict = {
    "alpha": "Alpha",
    "beta": "Beta",
    "rc": "Release Candidate"
}

date = datetime.date(int(__version__.build[1]), int(__version__.build[2]), int(__version__.build[3]))

def update_log():
    _update = """
    {}
    {}.{}: {}""".format(__name__, __version__.major, __version__.minor, _feature)
    if __version__.patch:
        _update += """
    Patch {}: {}""".format(__version__.patch, _patch)
    if __version__.prerelease[0]:
        _update += """
    {} {} (Development Phase {}): {}
    Changelog: {}
    Note that Development Builds can be unstable:
    Make sure to report bugs at https://github.com/Jefaxe/Kilt/issues""".format(
            prerelease_dict[__version__.prerelease[0]],
            __version__.prerelease[1],
            list(prerelease_dict.keys()).index(__version__.prerelease[0])+1,
            _commit,
            _changelog,)
    _update += """
    This build was made on {}""".format(date.strftime("%A, %d %B %Y"))
    return _update


def get_site():
    return "https://api.modrinth.com/api/v1/mod"


def get_query():
    return get_site() + "?query={}&limit={}&index={}&offset={}&filters={}"


def get_kilt_doc():
    return "https://github.com/Jefaxe/Kilt/wiki"


def get_labrinth_doc():
    return "https://github.com/modrinth/labrinth/wiki/API-Documentation"

print(update_log())
