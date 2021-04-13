## Kilt

- A Python Library / High end API for downloading / interacting with minecraft content.

# Installation  
## Latest:   
`git clone https://github.com/Jefaxe/Kilt.git`  
`cd Kilt`  
`pip install .` or `python setup.py install`   
## Stable:    
`pip install kilt`

# Usage
See the WIP [wiki](https://github.com/Jefaxe/Kilt/wiki)

# Changelog
See [CHANGELOG.md](https://github.com/Jefaxe/Kilt/blob/dev/CHANGELOG.md)
Note that versions prior to v0.1.0-beta.6 are very messed up should be ignored.

# Modules
Kilt is split into modules. They are `error` (for custom exceptions), `__init__` (needed),
`config` (for [runtime config](https://github.com/Jefaxe/Kilt/wiki/Runtime-Configuration)),
`version` (for data about the package version), `labrinth` (the main part)

## Structure

`kilt`  
`+--__init__.py: Needed`  
`+--config.py: `[Runtime Config](https://github.com/Jefaxe/Kilt/wiki/Runtime-Configuration)  
`+--error.py: Custom Exceptions for Kilt` [Source](https://github.com/Jefaxe/Kilt/blob/dev/kilt/error.py)       
`+--version.py: metadata`[Source](https://github.com/Jefaxe/Kilt/blob/dev/kilt/version.py)    
`+--labrinth.py: Modrinth API interaction` [Source](https://github.com/Jefaxe/Kilt/blob/dev/kilt/labrinth.py)  
`+--curse.py: (Planned for 0.2.0) Interaction with CurseForge via HTML scrapping (BeautifulSoup)`[Project](https://github.com/Jefaxe/Kilt/projects/1)    
`+--planetminecaft.py: (Planned 0.3.0) Interaction with PlanetMinecraft via HTML scrapping (BeautifulSoup)`[Project](https://github.com/Jefaxe/Kilt/projects/2)   
`+--common.py (Planned 0.2.0) Common code for all modules`