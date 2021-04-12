import semantic_version

__version__ = semantic_version.Version("0.1.0-beta.6")
__major__ = __version__.major
__minor__ = __version__.minor
__patch__ = __version__.patch
__prerelease__ = __version__.prerelease

_site = "https://api.modrinth.com/api/v1/mod"
_query = _site + "?query={}&limit={}&index={}&offset={}"
_doc = "https://github.com/Jefaxe/Kilt/wiki"