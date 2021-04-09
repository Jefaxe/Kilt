import webbrowser
import traceback
import json
import urllib.request
import logging
import os
import hashlib
import semantic_version
import kilt.errors
from PIL import Image

_site = "https://api.modrinth.com/api/v1/mod?query={}&limit={}&index={}&offset={}"


class VersionData:
    __version__ = semantic_version.Version("0.1.0-alpha1+api.1")
    __major__ = __version__.major
    __minor__ = __version__.minor
    __patch__ = __version__.patch
    __prerelease__ = __version__.prerelease
    __build__ = __version__.build


def alpha():
    if VersionData.__prerelease__[0] == "alpha":
        return True
    else:
        return False


def beta():
    if VersionData.__prerelease__[0] == "beta":
        return True
    else:
        return False


def api():
    return VersionData.__build__[1]


def release():
    if VersionData.__prerelease__[0] == "":
        return True
    else:
        return False


class Mod:
    def __init__(self, name, id, source, issues, desc, body, sha1=None, already_downloaded=False):
        self.sha1 = sha1
        self.name = name
        self.body = self.long_desc = body
        self.desc = desc
        self.id = id
        self.home = "https://modrinth.com/mod/{}".format(id)
        self.source = source
        self.issues = issues
        try:
            self.version = \
            json.loads(urllib.request.urlopen("https://api.modrinth.com/api/v1/mod/{}/version".format(self.id)).read())[
                0]["version_number"]
            self.loaders = \
                json.loads(
                    urllib.request.urlopen("https://api.modrinth.com/api/v1/mod/{}/version".format(self.id)).read())[
                    0]["loaders"]
            self.latest_mcversion = \
                json.loads(
                    urllib.request.urlopen("https://api.modrinth.com/api/v1/mod/{}/version".format(self.id)).read())[
                    0]["game_versions"][-1]
        except IndexError:  # there is no version
            self.version = None
            self.loaders = []
            self.latest_mcversion = None
        self.already_downloaded = already_downloaded
        self.isFabric = True if "fabric" in self.loaders else False
        self.isForge = True if "forge" in self.loaders else False
    def web_open(self, siteType):
        if siteType == "home":
            webbrowser.open(self.home)
            return True
        elif siteType == "source":
            webbrowser.open(self.source)
            return True
        elif siteType == "issues":
            webbrowser.open(self.issues)
            return True
        else:
            return False


is_source = is_src = alpha
is_github_release = beta
is_pypi_release = release


def get_sha1(filename):
    BLOCK_SIZE = 65536  # The size of each read from the file
    file_hash = hashlib.sha256()  # Create the hash object, can use something other than `.sha256()` if you wish
    with open(filename, 'rb') as f:  # Open the file to read it's bytes
        fb = f.read(BLOCK_SIZE)  # Read from the file. Take in the amount declared above
        while len(fb) > 0:  # While there is still data being read from the file
            file_hash.update(fb)  # Update the hash
            fb = f.read(BLOCK_SIZE)  # Read the next block from the file
    return file_hash.hexdigest()  # Get the hexadecimal digest of the hash


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
        return VersionData.__major__
    elif version_type == "minor":
        return VersionData.__minor__
    elif version_type == "patch":
        return VersionData.__patch__
    elif version_type == "prerelease":
        return VersionData.__prerelease__
    elif version_type == "build":
        return VersionData.__build__
    elif version_type == "full":
        return VersionData.__version__


def get_number_of_mods():
    number_of_mods = 0
    there_are_more_mods = True
    i = 0
    while there_are_more_mods:
        mod_list = json.loads(urllib.request.urlopen(_site.format("", 100, "newest", i * 100 + 1)).read())[
            "hits"]
        number_of_mods += len(mod_list)
        if len(mod_list) == 0:
            there_are_more_mods = False
        i += 1
    logging.info("There are {} mods on modrinth".format(number_of_mods))
    return number_of_mods


def search(search="", mod_id=None, id_array=[], saveIcon=False, logging_level=logging.INFO, crash=False, modlist=None,
           filemode="w", openweb=False, output=True, outputfile=None, index="relevance",
           offset=0,
           limit=10, saveDescriptionToFile=None, web_save=None, download_folder=None, search_array=[],
           repeat=1):
    # make sure arguments are correct
    failed_mods = []
    MOD_OBJECTS = []
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
        patched_searches.append(i.replace(" ", "%20"))
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
            logging.debug("Searching for {}".format(this_search))
            if mod_id is None:
                modSearch = _site.format(this_search, limit, index, offset)
                modSearchJson = json.loads(urllib.request.urlopen(modSearch).read())
                try:
                    logging.debug("{} is the {} in search_array".format(this_search, search_array.index(this_search)))
                    logging.debug(modSearchJson)
                    mod_response = modSearchJson["hits"][0]
                    logging.debug("{} is the mod_response of {}".format(mod_response, this_search))
                except IndexError:
                    if offset == 0 and repeat == 1:
                        logging.info("There were no results for your search")
                        raise kilt.errors.EndOfSearch("No results found for your query")
                    elif offset == 0 and repeat != 1:
                        logging.info("You hit the end of your search!")
                        raise kilt.errors.EndOfSearch(
                            "You attempted to access search result {} but {} was the max".format(offset + 1, offset))
                    else:
                        logging.info("Umm, you did a thing (I am confused at code)")
                modJsonURL = "https://api.modrinth.com/api/v1/mod/" + str(mod_response["mod_id"].replace("local-", ""))
            else:
                modJsonURL = "https://api.modrinth.com/api/v1/mod/" + mod_id
            logging.debug("Mod json URL: {}".format(modJsonURL))
            mod_struct = json.loads(urllib.request.urlopen(modJsonURL).read())
            mod_struct_minus_body = removekey(mod_struct, "body")
            mod_object = Mod(mod_struct_minus_body["title"], mod_struct_minus_body["id"],
                             mod_struct_minus_body["source_url"], mod_struct_minus_body["issues_url"],
                             mod_struct_minus_body["description"], mod_struct["body"])
            MOD_OBJECTS.append(mod_object)
            logging.debug("[Kilt] Mod Objects are: {}".format(MOD_OBJECTS))
            if saveIcon:
                os.makedirs("cache", exist_ok=True)
                if not os.path.exists("cache/{}.png".format(mod_struct_minus_body["title"])):
                    if mod_struct_minus_body["icon_url"] is None:
                        logging.debug("{} does not have a mod icon".format(mod_struct_minus_body["title"]))
                        mod_icon_fileLikeObject = urllib.request.urlopen("https://raw.githubusercontent.com/Jefaxe"
                                                                         "/Kilt/main/meta/missing.png")
                    else:
                        mod_icon_fileLikeObject = urllib.request.urlopen(str(mod_struct_minus_body["icon_url"]))
                    with open("cache/{}.png".format(mod_struct_minus_body["title"]), "wb") as file:
                        file.write(mod_icon_fileLikeObject.read())
                    basewidth = 64
                    img = Image.open('cache/{}.png'.format(mod_object.name))
                    wpercent = (basewidth / float(img.size[0]))
                    hsize = int((float(img.size[1]) * float(wpercent)))
                    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
                    img.save('cache/{}.png'.format(mod_object.name))
            logging.debug(
                "[Labrinth] Requested mod json(minus body): {json}".format(json=mod_struct_minus_body))
            # logging.debug("[Modrinth]: {json}".format(json=modSearchJson)
            # output events
            if saveDescriptionToFile is not None:
                with open(saveDescriptionToFile, "a") as desc:
                    desc.write(mod_struct_minus_body["title"] + ": " + mod_struct_minus_body["description"] + "\n")
            # web events
            if web_save is not None:
                page = mod_response["page_url"] if web_save == "home" else mod_struct_minus_body[
                    dict_of_pages[web_save]]
                if openweb and page not in [None, [], ""]:
                    webbrowser.open(page)
                    logging.debug(
                        "[Knosses] Opened {}'s {} page at {}".format(mod_struct_minus_body["title"], web_save, page))
            try:
                downloadLink = \
                    json.loads(urllib.request.urlopen("{json}/version".format(json=modJsonURL)).read())[0]["files"][0][
                        "url"].replace(" ", "%20")
            except IndexError:
                logging.error("mod {} does not have any versions, skipping...".format(mod_response["title"]))
                downloadLink = "https://modrinth.com/download-was-not-found-by-kilt"
                failed_mods.append(mod_response["title"])
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
                            mod_object.already_downloaded = True
                            mod_object.sha1 = get_sha1(
                                download_folder + "/{mod}".format(mod=downloadLink.rsplit("/", 1)[-1]).replace("%20",
                                                                                                               " "))
                    except UnboundLocalError:
                        pass
                    else:
                        logging.info(
                            "[Kilt] Downloading {mod} from {url}".format(mod=mod_struct_minus_body["title"],
                                                                         url=downloadLink))
                        downloadUrrlib = urllib.request.urlopen(downloadLink)
                        with open(download_folder + "/{mod}".format(mod=downloadLink.rsplit("/", 1)[-1]).replace("%20",
                                                                                                                 " "),
                                  "wb") as modsave:
                            modsave.write(downloadUrrlib.read())
                        mod_object.sha1 = get_sha1(
                            download_folder + "/{mod}".format(mod=downloadLink.rsplit("/", 1)[-1]).replace("%20", " "))
                except urllib.error.HTTPError as e:
                    logging.critical(
                        "[Labrinth] COULD NOT DOWNLOAD MOD {} from {} because {}".format(mod_response["title"],
                                                                                         downloadLink, e))
                    failed_mods.append(mod_response["title"])
            if modlist is not None:
                with open(modlist, "a") as file:
                    file.write(
                        "<image src={} width=64 height=64 alt={}><a href={}>{} (by {}):      </a><a href={}>Download<p></p>".format(
                            mod_struct_minus_body["icon_url"],
                            mod_struct_minus_body["title"],
                            mod_response["page_url"],
                            mod_struct_minus_body["title"],
                            mod_response["author"],
                            downloadLink))
        offset += 1
    if modlist is not None:
        with open(modlist, "a") as file:
            file.write(""" </body>
</html>""")
    return MOD_OBJECTS


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
