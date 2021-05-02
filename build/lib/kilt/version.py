import os

import semantic_version
import datetime

__version__ = semantic_version.Version("0.1.0-rc.4+build.2021.05.02")
_patch_note = None
_commit = "Bug Fixes yay!"
_changelog = """Removed mutable objects in function arguments"""

prerelease_dict = {
    "alpha": "Alpha",
    "beta": "Beta",
    "rc": "Release Candidate"
}

date = datetime.date(int(__version__.build[1]), int(__version__.build[2]), int(__version__.build[3]))


def update_log(outputfile=False, append_build=False):
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

    os.makedirs("version/", exist_ok=True)
    with open(f"version/{__version__}.txt", "w") as fp:
            fp.write(_update)
    return _update


labrinth_mod = "https://api.modrinth.com/api/v1/mod"

kilt_doc = "https://github.com/Jefaxe/Kilt/wiki"

labrinth_doc = "https://github.com/modrinth/labrinth/wiki/API-Documentation"

if __name__ == "__main__":
    print(update_log())
