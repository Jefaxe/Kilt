import semantic_version
import datetime

__version__ = semantic_version.Version("0.1.0-rc.3+build.2021.04.24")
_patch_note = None
_commit = "It should be ready..."
_changelog = """Incremented version
    Fixed Issues created in beta 7.1 & 8
    labrinth.get_number_of_mods now just uses the modrinth-supplied 'total_hits'. (I am an idiot, i was counting them before lol)"""

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
        _update += "Patch {}\n: {}".format(__version__.patch, _patch_note)
    _update += "Changelog: {}".format(_changelog)
    if len(__version__.prerelease):
        _update += """
        Note that Development Builds can be unstable:
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

if __name__ == "__main__":
    print(update_log())
