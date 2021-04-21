import semantic_version
import datetime

__version__ = semantic_version.Version("0.1.0-beta.8+build.2021.04.21")
__name__ = "Kilt"
_feature = "Initial release; modrinth support"
_patch = None
_commit = "Added facets support"
_changelog = """
        Added full facets support for searching. """

prerelease_dict = {
    "alpha": "Alpha",
    "beta": "Beta",
    "rc": "Release Candidate"
}

date = datetime.date(int(__version__.build[1]), int(__version__.build[2]), int(__version__.build[3]))


def update_log(outputfile=False):
    _update = """{commit}
    {version}
    """.format(
        commit=_commit,
        version=str(__version__.major) + "." + str(__version__.minor) + (" " + prerelease_dict[__version__.prerelease[0]] + " " + str(
            ".".join(__version__.prerelease[1:])) if len(__version__.prerelease) else "")
    )
    if __version__.patch != 0:
        _update += "Patch {}\n".format(__version__.patch)
    _update += "Changelog: {}\n".format(_changelog)
    if len(__version__.prerelease):
        _update += """Note that Development Builds can be unstable:
        Make sure to report bugs at https://github.com/Jefaxe/Kilt/issues"""
    _update += """
    This build was made on {}""".format(date.strftime("%A, %d %B %Y"))
    if outputfile:
        with open(outputfile, "w") as fp:
            fp.write(_update)
    return _update


labrinth_mod = "https://api.modrinth.com/api/v1/mod"

kilt_doc = "https://github.com/Jefaxe/Kilt/wiki"

labrinth_doc = "https://github.com/modrinth/labrinth/wiki/API-Documentation"
