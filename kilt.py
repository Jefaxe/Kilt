import argparse
import hashlib
import json
import logging
import os
import sys
import traceback
import urllib.request
import webbrowser


class Kilt:
    __version__ = "0.2.1"


def remove_key(d, key):
    r = dict(d)
    del r[key]
    return r


def main():
    # valueToReturn=None
    # sets arguments
    parser = argparse.ArgumentParser(description='A program used to interact with the Modrinth API aka Labrinth')
    # output
    parser.add_argument("-ml", "--modlist",
                        help="Generate a modlist.html file. This file can be changed by specifying it after --modlist/-ml, which can include a path.",
                        nargs="?", const="modlist.html")
    parser.add_argument("-lg", "--logging", help="Set the logging value. Defaults to INFO", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"])
    parser.add_argument("-fm", "--filemode",
                        help="Sets the filemode. Defaults to a/append, if -afm/--filemode is given, else defaults to w/write.",
                        nargs="?", default="w", const="a")
    parser.add_argument("-ow", "--openweb",
                        help="Open the web browser --open instead of just returning the URL",
                        action="store_true")
    parser.add_argument("-m", "--modjson",
                        help="Return ONLY the mod json, not the entire search json. This overrides normal return data/",
                        action="store_true")
    parser.add_argument("-sj", "--searchjson",
                        help="Return ONLY the search json, the not specific mod json. This overrides normal return data.",
                        action="store_true")
    parser.add_argument("-no", "--no_output",
                        help="DOESN'T Display the result in console.  Use --fileoutput to save to a file",
                        action="store_false")
    parser.add_argument("-f", "--outputfile", help="Send the output to a file")
    parser.add_argument("-ds", "--dontMentionSearch", help="Don't show the 'Searching using...' message in log",
                        action="store_true")
    # filters
    parser.add_argument("-i", "--index", help="How to filter the mods. (newest,updated,relevance,downloads)",
                        default="newest")
    parser.add_argument("-p", "--place", help="What location down the list to look for the mod?(default: 0 (top))",
                        default=0, type=int)
    parser.add_argument("-l", "--limit", help="Sets the number of mods that will be checked(default: 10)", default=10,
                        type=int)
    # parser.add_argument("-cmc","--configureMC",help="Temporarily configure the minecraft version used for searching mods",default=config)
    # output events
    parser.add_argument("-D", "--description",
                        help="Saves the (short) description of the mod to the specified location. Defeats to descs.txt. Note that it appends to the file.",
                        nargs="?", const="descs.txt")
    # web events
    parser.add_argument("-H", "--open", help="Save (open with --openweb aswell) a mod link, like issues")
    # downloads
    parser.add_argument("-d", "--download", help="Downloads the requested mod to the requested path.", nargs="?",
                        const="mods")
    parser.add_argument("-b", "--body", action="store_true",
                        help="Downloads the description.md file for the requested mod. Only really useful when you have a .md viewer, like Markdown View")
    # meta
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("-r", "--repeat", help="Repeat specified number of times, rising args.place by 1 each time.",
                        default=1, type=int)
    parser.add_argument("-g", "--get",
                        help="Gets a list of vanity's for a given search. Use an argument to specify a file. (modlist.txt by default).",
                        nargs="?", const="modlist.txt")
    group.add_argument("-fs", "--file_to_search", help="File to get searches from. Incompatible with --search")
    parser.add_argument("-dir", "--directory", help="set working directory. Defaults to current working directory",
                        default=".")
    group.add_argument("-q", "--search", help="Simply search modrith . -q stands for query", default="")
    group.add_argument("-v", "--version", help="show current version and exit", action="store_true")
    # completes setting of arguments
    args = parser.parse_args()
    # if no arguments are passed, show the help screen
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return "HELP"
    args = parser.parse_args()
    if args.version:
        print(Kilt.__version__)
        if __name__ == "__main__":
            sys.exit("Kilt version is {ver}".format(ver=Kilt.__version__))
    # print(args.download)
    os.chdir(args.directory)
    # sets up logging
    args.logging = args.logging.upper()
    logs_dict = {
        "NOTSET": 0,
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50}
    logging_file = "kilt.log"
    logging_format = '[%(funcName)s/%(levelname)s] %(message)s'
    logging_level = logs_dict[args.logging]
    logging.basicConfig(filename=logging_file, level=logging_level, format=logging_format, filemode=args.filemode)
    ###
    # searching of mods
    ##
    searches = []
    site = "https://api.modrinth.com/api/v1/mod?query={whatmod}&limit={limit}&index={sort}&offset={place}"
    if args.file_to_search is not None:
        with open(args.file_to_search) as file:
            searches = file.readlines()
    else:
        if args.search != "":
            args.index = "relevance"
        searches.append(args.search)
    patched_searches = []
    for SEARCH in searches:
        SEARCH = SEARCH.replace("\n", "")
        patched_searches.append(SEARCH)
    searches = patched_searches
    # print(searches)
    if not args.dontMentionSearch:
        logging.debug("Mods to search for: {}".format(" ,".join(searches)))
    if args.modlist is not None:
        with open(args.modlist, "w") as file:
            file.write("<ul>")
    if args.get is not None:
        with open(args.get, "w") as file:
            file.write("")
    for i in range(args.repeat):
        for this_mod in searches:
            modSearch = site.format(whatmod=this_mod, limit=args.limit, sort=args.index, place=args.place).replace(" ",
                                                                                                                   "%20")
            modSearchJson = json.loads(urllib.request.urlopen(modSearch).read())
            # print(modSearchJson)
            try:
                mod_response = modSearchJson["hits"][0]
            except IndexError:  # if the search resulted in nothing
                return "search_ended"
            modJsonURL = "https://api.modrinth.com/api/v1/mod/" + str(mod_response["mod_id"].replace("local-", ""))
            mod_struct = json.loads(urllib.request.urlopen(modJsonURL).read())
            mod_struct_minus_body = remove_key(mod_struct, "body")
            logging.debug(
                "[Modrinth/Labrinth] Requested mod json(minus body): {json}".format(json=mod_struct_minus_body))
            # logging.debug("[Modrinth]: {json}".format(json=modSearchJson))
            if args.place >= modSearchJson['total_hits']:
                logging.error(
                    "There are not THAT many in the search, set --limit in launch higher. Or that may be it all. NOTE THAT ARGS.PLACE WILL BE SET TO 0")
                args.place = 0
            valueToReturn = mod_struct_minus_body
            # output events
            if args.description is not None:
                with open(args.description, "a") as desc:
                    desc.write(mod_struct["title"] + ": " + mod_struct["description"] + "\n")
            if args.get is not None:
                with open(args.get, "a") as file:
                    file.write(mod_struct["title"] + "\n")
            # web events
            if args.open is not None:
                # print(args.open)
                dict_of_pages = {
                    "issues": 'issues_url',
                    "source": 'source_url',
                    "wiki": 'wiki_url',
                    "discord": "discord_url",
                    "donation": "donation_urls"
                }
                page = mod_response["page_url"] if args.open == "home" else mod_struct[dict_of_pages[args.open]]

                if args.openweb and page not in [None, [], ""]:
                    webbrowser.open(page)
                valueToReturn = page

            # downloads
            if args.download is not None:
                os.makedirs(str(args.download), exist_ok=True)
                filename = \
                    json.loads(urllib.request.urlopen("{json}/version".format(json=modJsonURL)).read())[0]["files"][0][
                        "filename"]
                if filename in os.listdir(args.download):
                    logging.info(
                        "{} is already downloaded (note we have only checked the filename, not the SHA1 hash".format(
                            filename))
                    valueToReturn = "the_file_is_already_downloaded"
                else:
                    downloadLink = \
                        json.loads(urllib.request.urlopen("{json}/version".format(json=modJsonURL)).read())[0]["files"][
                            0][
                            "url"].replace(" ", "%20")
                    logging.info(
                        "[Kilt] Downloading {mod} from {url}".format(mod=mod_struct["title"], url=downloadLink))
                    download = urllib.request.urlopen(downloadLink)
                    with open(args.download + "/{mod}".format(mod=downloadLink.rsplit("/", 1)[-1]).replace("%20", " "),
                              "wb") as modsave:
                        modsave.write(download.read())
                    BLOCK_SIZE = 65536  # The size of each read from the file
                    file_hash = hashlib.sha256()  # Create the hash object, can use something other than `.sha256()` if you wish
                    with open(args.download + "/{mod}".format(mod=downloadLink.rsplit("/", 1)[-1]).replace("%20", " "),
                              'rb') as f:  # Open the file to read it's bytes
                        fb = f.read(BLOCK_SIZE)  # Read from the file. Take in the amount declared above
                        while len(fb) > 0:  # While there is still data being read from the file
                            file_hash.update(fb)  # Update the hash
                            fb = f.read(BLOCK_SIZE)  # Read the next block from the file
                    valueToReturn = file_hash.hexdigest()  # Get the hexadecimal digest of the hash
                if args.modlist is not None:
                    with open(args.modlist, "w") as file:
                        file.write(
                            '<li><a href="{}">{} (by {})</a></li>'.format(mod_response["page_url"], mod_struct["title"],
                                                                          mod_response["author"]))
            if args.body:
                with open("generated/meta/{mod}".format(mod=mod_struct["title"] + ".md"), "w") as modsave:
                    modsave.write(mod_struct["body"])
                    valueToReturn = mod_struct["body"]
            if args.modjson:
                valueToReturn = mod_struct
            if args.searchjson:
                valueToReturn = args.searchjson
            if not args.no_output:
                print(valueToReturn)
            if args.outputfile is not None:
                with open(args.outputfile, "w") as file:
                    for i in [valueToReturn]:
                        json.dump(i, file, indent=4)
        args.place += 1
    if args.modlist is not None:
        with open(args.modlist, "a") as file:
            file.write("</ul>")
    return valueToReturn


if __name__ == "__main__":
    try:
        main()
    except (Exception, SystemExit) as e:
        if type(e) == SystemExit:
            print(e)
        else:
            traceback.format_exc(str(e))
            print(e)
            print("The process ran into an error. The error can be found in kilt.log")
