# Kilt
A command line interface (CLI) that implements the Modrinth API.

usage: kilt.py [-h] [-q SEARCH] [-i INDEX] [-p PLACE] [-l LIMIT]
               [-cmc CONFIGUREMC] [-D DESCRIPTION] [-H] [-is] [-s] [-d] [-b]

Searches modrinth

optional arguments:
  -h, --help            show this help message and exit
  -q SEARCH, --search SEARCH
                        Simply search modrith (mod name in URL, NOT ID). -q
                        stands for query
  -i INDEX, --index INDEX
                        How to filter the mods.
                        (newest,updated,relevance,downloads)
  -p PLACE, --place PLACE
                        What location down the list to look for the
                        mod?(default: 0 (top))
  -l LIMIT, --limit LIMIT
                        Sets the number of mods that will be checked(default:
                        10)
  -cmc CONFIGUREMC, --configureMC CONFIGUREMC
                        Temparerily configure the minecraft version used for
                        searching mods
  -D DESCRIPTION, --description DESCRIPTION
                        Shows the description of the mod on screen (with
                        'console'), or saves it generated/descriptions.txt
                        with 'saveToFile'
  -H, --home            Opens the homepage of the mod
  -is, --issues         Report bugs and suggest features here!
  -s, --source          Visit the source code page of the mod
  -d, --download        Downloads the requested mod
  -b, --body            Downloads the description.md file for the requested
                        mod. Only really useful when you have a .md vewier,
                        like Markdown View
>>> 


Search differs from "vanilla" modrinth search in one way. When using a command, but not searching anything, the index will be set to `newest` instead of `relevance` so that searching can acaully change. Also useful to download the latest mods.
