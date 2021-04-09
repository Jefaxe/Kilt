import webbrowser
import traceback
import json
import urllib.request
import logging
import os
import hashlib
import semantic_version
import kilt.errors

class versionData:
    site = "https://api.modrinth.com/api/v1/mod?query={}&limit={}&index={}&offset={}"
    __version__ = semantic_version.Version("0.1.0-alpha0+api.1")
    __major__ = __version__.major
    __minor__ = __version__.minor
    __patch__ = __version__.patch
    __prerelease__ = __version__.prerelease
    __build__ = __version__.build


def alpha():
    if versionData.__prerelease__[0] == "alpha":
        return True
    else:
        return False


def beta():
    if versionData.__prerelease__[0] == "beta":
        return True
    else:
        return False


def api():
    return versionData.__build__[1]


def release():
    if versionData.__prerelease__[0] == "":
        return True
    else:
        return False


is_source = is_src = alpha
is_github_release = beta
is_pypi_release = release



class ReturnValues:
    mod_exists_already = "mod_exists_already"

    # sets up logging
    if not os.path.exists("logs/"):
        os.mkdir("logs")
    logging_format = '[%(filename)s][%(funcName)s/%(levelname)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG, filename="logs/debug.log", filemode="w", format=logging_format)


def removekey(d, key):
    r = dict(d)
    del r[key]
    return r


def get_version(version_type="full"):
    if version_type == "major":
        return versionData.__major__
    elif version_type == "minor":
        return versionData.__minor__
    elif version_type == "patch":
        return versionData.__patch__
    elif version_type == "prerelease":
        return versionData.__prerelease__
    elif version_type == "build":
        return versionData.__build__
    elif version_type == "full":
        return versionData.__version__


def get_number_of_mods():
    number_of_mods = 0
    there_are_more_mods = True
    i = 0
    while there_are_more_mods:
        mod_list = json.loads(urllib.request.urlopen(versionData.site.format("", 100, "newest", i * 100 + 1)).read())[
            "hits"]
        number_of_mods += len(mod_list)
        if len(mod_list) == 0:
            there_are_more_mods = False
        i += 1
    logging.info("There are {} mods on modrinth".format(number_of_mods))
    return number_of_mods


def search(id=None, id_array=[], get=True, saveIcon=False, logging_level=logging.INFO, crash=False, modlist=None, filemode="w", openweb=False, output=True, outputfile=None, index="relevance",
           offset=0,
           limit=10, saveDescriptionToFile=None, web_save=None, download_folder=None, body=False, search_array=[],
           repeat=1, search=""):
    # make sure arguments are correct
    failed_mods = []
    valueToReturn = None
    extra_values = []
    dict_of_pages = {
        "issues": 'issues_url',
        "source": 'source_url',
        "wiki": 'wiki_url',
        "discord": "discord_url",
        "donation": "donation_urls"
    }
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    if type(saveIcon) is not bool:
        raise kilt.errors.InvalidArgument("{} (saveIcon) is not a boolean".format(saveIcon))
    if type(limit) is not int or limit not in list(range(0, 101)):
        raise kilt.errors.InvalidArgument("{} (limit) is not in range 0, 100, or is not an integer.".format(limit))
    if web_save not in list(dict_of_pages.keys()) and web_save not in {"home", None}:
        raise kilt.errors.InvalidArgument(
            "{} (web_save) is not in {}".format(web_save, (list(dict_of_pages.keys()), "home")))
    if type(crash) is not bool:
        raise kilt.errors.InvalidArgument("{} (crash) is not a boolean".format(crash))
    if filemode not in {"w", "a"}:
        raise kilt.errors.InvalidArgument("{} (filemode) is not in 'a' or 'w'".format(filemode))
    if type(openweb) is not bool:
        raise kilt.errors.InvalidArgument("{} (openweb) is not a boolean".format(openweb))
    if type(output) is not bool:
        raise kilt.errors.InvalidArgument("{} (output) is not a boolean".format(output))
    if type(offset) is not int or offset not in list(range(0, 101)):
        raise kilt.errors.InvalidArgument("{} (offset) is not in range 0, 100, or it is not an integer".format(offset))
    if type(body) is not bool:
        raise kilt.errors.InvalidArgument("{} (body) is not a boolean".format(body))
    if type(repeat) is not int or repeat <= 0:
        raise kilt.errors.InvalidArgument("{} (repeat) is not an integer, or it is below 0.".format(repeat))
    ###
    # searching of mods
    ##
    if not search_array:
        if search == "":
            index = "newest"
        search_array.append(search)
    patched_searches = []
    for i in search_array:
        patched_searches.append(i.replace(" ","%20"))
    search_array = patched_searches
    logging.info("Mods to search for: {}".format(" ,".join(search_array)))
    if saveDescriptionToFile is not None:
        with open(saveDescriptionToFile, "w") as file:
            file.write("Mod Descriptions\n")
    if modlist is not None:
        with open(modlist, "w") as file:
            file.write("""<!DOCTYPE html>
                        <html>
                                <head>
                                        <title>Modlist</title>
                                </head>

                                <body>""")
    for this_fake_var in range(repeat):
        for this_search in search_array:
            if id is None:
                modSearch = versionData.site.format(this_search, limit, index, offset)
                modSearchJson = json.loads(urllib.request.urlopen(modSearch).read())
                try:
                    mod_response = modSearchJson["hits"][0]
                except IndexError:
                    if offset == 0 and repeat == 1:
                        logging.info("There were no results for your search")
                        raise kilt.errors.EndOfSearch("No results found for your query")
                    elif offset == 0 and repeat != 1:
                        logging.info("You hit the end of your search!")
                        raise kilt.errors.EndOfSearch("You attempted to access search result {} but {} was the max".format(offset+1, offset))
                    else:
                        break
                modJsonURL = "https://api.modrinth.com/api/v1/mod/" + str(mod_response["mod_id"].replace("local-", ""))
            else:
                modJsonURL = "https://api.modrinth.com/api/v1/mod/" + id
            mod_struct = json.loads(urllib.request.urlopen(modJsonURL).read())
            if not get:
                extra_values = mod_struct
            if get:
                try:
                    extra_values.append({"title": mod_struct["title"], "url": "https://modrinth.com/mod/{}".format(mod_struct["slug"]),
                                      "desc": mod_struct["description"], "id": mod_struct["id"]})
                except AttributeError:
                    pass
            if saveIcon:
                os.makedirs("cache", exist_ok=True)
                if not os.path.exists("cache/{}.png".format(mod_struct["title"])):
                    if mod_struct["icon_url"] is None:
                        logging.debug("{} does not have a mod icon".format(mod_struct["title"]))
                        mod_icon_fileLikeObject = urllib.request.urlopen("https://raw.githubusercontent.com/Jefaxe"
                                                                         "/Kilt/main/meta/missing.png")
                    else:
                        mod_icon_fileLikeObject = urllib.request.urlopen(str(mod_struct["icon_url"]))
                    with open("cache/{}.png".format(mod_struct["title"]), "wb") as file:
                        file.write(mod_icon_fileLikeObject.read())
            mod_struct_minus_body = removekey(mod_struct, "body")
            logging.debug(
                "[Labrinth] Requested mod json(minus body): {json}".format(json=mod_struct_minus_body))
            # logging.debug("[Modrinth]: {json}".format(json=modSearchJson))
            try:
                if offset >= modSearchJson['total_hits']:
                    logging.error(
                        "There are not THAT many in the search, set `limit` higher. Or that may be it all. NOTE THAT `offset` WILL BE SET TO 0")
                    offset = 0
            except UnboundLocalError: #when using 'id', modSearchJson is not defined
                pass
            # output events
            if saveDescriptionToFile is not None:
                with open(saveDescriptionToFile, "a") as desc:
                    desc.write(mod_struct["title"] + ": " + mod_struct["description"] + "\n")
            # web events
            if web_save is not None:
                page = mod_response["page_url"] if web_save == "home" else mod_struct[dict_of_pages[web_save]]
                if openweb and page not in [None, [], ""]:
                    webbrowser.open(page)
                    logging.debug("[Knosses] Opened {}'s {} page at {}".format(mod_struct["title"], web_save, page))
                valueToReturn = page
            try:
                downloadLink = \
                    json.loads(urllib.request.urlopen("{json}/version".format(json=modJsonURL)).read())[0]["files"][0][
                        "url"].replace(" ", "%20")
            except IndexError:
                logging.error("mod {} does not have any versions, skipping...".format(mod_response["title"]))
                downloadLink="https://modrinth.com/download-was-not-found-by-kilt"
                failed_mods.append(mod_response["title"])
                valueToReturn = failed_mods
            # downloads
            if download_folder is not None:
                if type(download_folder) == bool and download_folder:
                    download_folder = "mods"
                try:
                    os.makedirs(download_folder, exist_ok=True)
                    try:
                        filename = \
                            json.loads(urllib.request.urlopen("{json}/version".format(json=modJsonURL)).read())[0][
                                "files"][0][
                                "filename"]
                    except IndexError:
                        logging.error("mod {} has no versions".format(mod_response["title"]))
                    try:
                        if filename in os.listdir(download_folder):
                            logging.info(
                                "[Kilt]{} is already downloaded (note we have only checked the filename, not the SHA1 hash".format(
                                    filename))
                            if crash:
                                raise errors.AlreadyDownloaded("{}".format(filename))
                            else:
                                valueToReturn = ReturnValues.mod_exists_already
                    except UnboundLocalError:
                        pass
                    else:
                        logging.info(
                            "[Kilt] Downloading {mod} from {url}".format(mod=mod_struct["title"], url=downloadLink))
                        downloadUrrlib = urllib.request.urlopen(downloadLink)
                        with open(download_folder + "/{mod}".format(mod=downloadLink.rsplit("/", 1)[-1]).replace("%20",
                                                                                                                 " "),
                                  "wb") as modsave:
                            modsave.write(downloadUrrlib.read())
                        BLOCK_SIZE = 65536  # The size of each read from the file
                        file_hash = hashlib.sha256()  # Create the hash object, can use something other than `.sha256()` if you wish
                        with open(download_folder + "/{mod}".format(mod=downloadLink.rsplit("/", 1)[-1]).replace("%20",
                                                                                                                 " "),
                                  'rb') as f:  # Open the file to read it's bytes
                            fb = f.read(BLOCK_SIZE)  # Read from the file. Take in the amount declared above
                            while len(fb) > 0:  # While there is still data being read from the file
                                file_hash.update(fb)  # Update the hash
                                fb = f.read(BLOCK_SIZE)  # Read the next block from the file
                        valueToReturn = file_hash.hexdigest()  # Get the hexadecimal digest of the hash
                except urllib.error.HTTPError as e:
                    logging.critical(
                        "[Labrinth] COULD NOT DOWNLOAD MOD {} from {} because {}".format(mod_response["title"],
                                                                                         downloadLink, e))
                    failed_mods.append(mod_response["title"])
                    valueToReturn = failed_mods
            if modlist is not None:
                with open(modlist, "a") as file:
                    file.write(
                        "<image src={} width=64 height=64 alt={}><a href={}>{} (by {}):      </a><a href={}>Download<p></p>".format(
                            mod_struct["icon_url"],
                            mod_struct["title"],
                            mod_response["page_url"],
                            mod_struct["title"],
                            mod_response["author"],
                            downloadLink))
            if body:
                with open("generated/meta/{mod}".format(mod=mod_struct["title"] + ".md"), "w") as modsave:
                    modsave.write(mod_struct["body"])
                    valueToReturn = mod_struct["body"]
            if not output:
                print(valueToReturn)
            if outputfile is not None:
                with open(outputfile, "w") as file:
                    for x in [valueToReturn]:
                        json.dump(x, file, indent=4)
            offset += 1
    if modlist is not None:
        with open(modlist, "a") as file:
            file.write(""" </body>
</html>""")
    #logging.info(extra_values)
    return [valueToReturn, extra_values]


if __name__ == "__main__":
    try:
        search()
    except (Exception, SystemExit) as e:
        if type(e) == SystemExit:
            print(e)
        else:
            logging.error(traceback.format_exc())
            print(e)
            print("The process ran into an error. The error can be found in version_data.log")
