import webbrowser
import traceback
import json
import urllib.request
import logging
import os
import hashlib
import semantic_version
import kilt.error
from PIL import Image

# sets up logging
logging.basicConfig()


class VersionData:
    __version__ = semantic_version.Version("0.1.0-alpha.2+labrinth.1")
    __major__ = __version__.major
    __minor__ = __version__.minor
    __patch__ = __version__.patch
    __prerelease__ = __version__.prerelease
    __build__ = __version__.build


_site = "https://api.modrinth.com/api/v{}".format(VersionData.__build__[1])
_query = _site + "/mod?query={}&limit={}&index={}&offset={}"
_doc = "https://github.com/Jefaxe/Kilt/wiki"
_pypi = None


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
    def __init__(self, name, id, source, issues, desc, body):
        self.sha1 = None
        self.downloaded = False
        self.name = name
        self.body = self.long_desc = body
        self.desc = desc
        self.id = id
        self.home = "https://modrinth.com/mod/{}".format(id)
        self.source = source
        self.issues = issues
        try:
            self.version = \
                json.loads(
                    urllib.request.urlopen("https://api.modrinth.com/api/v1/mod/{}/version".format(self.id)).read())[
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
        self.isFabric = self.is_fabric = True if "fabric" in self.loaders else False
        self.isForge = self.is_fabric = True if "forge" in self.loaders else False

    def save_icon(self, path=None, createTree=False):
        if path is None:
            path = "cache/"+self.name+".png"
        icon_url = json.loads(urllib.request.urlopen(_site+"/mod/"+self.id).read())["icon_url"]
        if createTree:
            os.makedirs("".join(path.rsplit("/", 1)[:-1]))
        with open(path, "wb") as file:
            file.write(urllib.request.urlopen(icon_url).read())

    def web_open(self, siteType="home"):
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

    def download(self, download_folder="mods", specific_version=None):
        # downloads
        try:
            os.makedirs(download_folder, exist_ok=True)
            try:
                if specific_version is not None:
                    found = False
                    index_value = 0
                    for i in json.loads(urllib.request.urlopen(_site + "/mod/" + self.id + "/version").read()):
                        logging.debug(i["version_number"])
                        if i["version_number"] == specific_version:
                            mod_version = json.loads(urllib.request.urlopen(_site + "/mod/" + self.id + "/version").read())[index_value][
                                "files"][0]
                            found = True
                        index_value += 1
                    if not found:
                        raise kilt.error.SpecificVersionNotFound("{} is not a version of '{}'".format(specific_version, self.name))
                else:
                    mod_version = json.loads(urllib.request.urlopen(_site + "/mod/" + self.id + "/version").read())[0][
                        "files"][0]
                filename = mod_version["filename"]
                downloadLink = mod_version[
                        "url"]
                self.sha1 = mod_version["hashes"][
                        "sha1"]
            except IndexError:
                raise kilt.error.NoVersionFound("mod '{}' has no versions".format(self.name))
            try:
                if filename in os.listdir(download_folder):
                    logging.debug(
                        "[Kilt]{} is already downloaded (note we have only checked the filename, not the SHA1 hash".format(
                            filename))
            except UnboundLocalError:
                pass
            else:
                logging.info(
                    "[Kilt] Downloading {mod} from {url}".format(mod=self.name,
                                                                 url=downloadLink))
                downloadUrrlib = urllib.request.urlopen(downloadLink)
                with open(download_folder + "/{mod}".format(mod=downloadLink.rsplit("/", 1)[-1]).replace("%20",
                                                                                                         " "),
                          "wb") as modsave:
                    modsave.write(downloadUrrlib.read())
            self.downloaded = True
        except urllib.error.HTTPError as e:
            logging.critical(
                "[Labrinth] COULD NOT DOWNLOAD MOD {} from {} because {}".format(self.name,
                                                                                 downloadLink, e))


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
        mod_list = json.loads(urllib.request.urlopen(_query.format("", 100, "newest", i * 100 + 1)).read())[
            "hits"]
        number_of_mods += len(mod_list)
        if len(mod_list) == 0:
            there_are_more_mods = False
        i += 1
    logging.info("There are {} mods on modrinth".format(number_of_mods))
    return number_of_mods


def search(search="", mod_id=None, saveIcon="dep", logging_level=logging.WARNING, modlist=None,
           openweb="dep", index="relevance",
           offset=0,
           limit=10, saveDescriptionToFile=None, web_save="dep", search_array=[],
           repeat=1, download_folder="dep"):
    # make sure arguments are correct
    MOD_OBJECTS = []
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    if index not in {"newest", "updated", "downloads", "relevance"}:
        raise kilt.error.InvalidArgument("{} (index/sort) needs to be either 'newest', 'updated', 'downloads', or 'relevance'".format(index))
    if type(limit) is not int or limit not in list(range(0, 101)):
        raise kilt.error.InvalidArgument("{} (limit) is not in range 0, 100, or is not an integer.".format(limit))
    if type(offset) is not int or offset not in list(range(0, 101)):
        raise kilt.error.InvalidArgument("{} (offset) is not in range 0, 100, or it is not an integer".format(offset))
    if type(repeat) is not int or repeat <= 0:
        raise kilt.error.InvalidArgument("{} (repeat) is not an integer, or it is below 0.".format(repeat))
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
    logging.debug("Mods to search for: {}".format(" ,".join(search_array)))
    if saveDescriptionToFile is not None:
        with open(saveDescriptionToFile, "w") as file:
            file.write("Mod Descriptions\n")
    if modlist is not None:
        if type(modlist) is bool and modlist:
            modlist = "modlist.html"
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
                modSearch = _query.format(this_search, limit, index, offset)
                modSearchJson = json.loads(urllib.request.urlopen(modSearch).read())
                try:
                    logging.debug("{} is the {} in search_array".format(this_search, search_array.index(this_search)))
                    logging.debug(modSearchJson)
                    mod_response = modSearchJson["hits"][0]
                    logging.debug("{} is the mod_response of {}".format(mod_response, this_search))
                except IndexError:
                    if offset == 0 and repeat == 1:
                        logging.info("There were no results for your search")
                        raise kilt.error.EndOfSearch("No results found for your query")
                    elif offset == 0 and repeat != 1:
                        logging.info("You hit the end of your search!")
                        raise kilt.error.EndOfSearch(
                            "You attempted to access search result {} but {} was the max".format(offset + 1, offset))
                    else:
                        logging.info("Umm, you did a thing (I am confused at code)")
                modJsonURL = "https://api.modrinth.com/api/v1/mod/" + str(mod_response["mod_id"].replace("local-", ""))
            else:
                modJsonURL = "https://api.modrinth.com/api/v1/mod/" + mod_id
            logging.debug("Mod json URL: {}".format(modJsonURL))
            try:
                mod_struct = json.loads(urllib.request.urlopen(modJsonURL).read())
            except urllib.error.HTTPError:
                raise kilt.error.InvalidModId("{} is not a valid modinth mod id".format(mod_id))
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

            if modlist is not None:
                with open(modlist, "a") as file:
                    file.write(
                        "<image src={} width=64 height=64 alt={}><a href={}>{} (by {}):      </a>".format(
                            mod_struct_minus_body["icon_url"],
                            mod_struct_minus_body["title"],
                            mod_response["page_url"],
                            mod_struct_minus_body["title"],
                            mod_response["author"]))
            # deprecation warnings!
            if download_folder != "dep":
                logging.critical("DEPRECATION! DO NOT USE 'download_folder' ARGUMENT, USE METHOD `.download()` ON MOD OBJECT!  ")
                if type(download_folder) is bool and download_folder:
                    download_folder = "mods"
                mod_object.download(download_folder=download_folder)
            if web_save != "dep":
                logging.critical("DEPRECATION! DO NOT USE 'web_save' ARGUMENT, USE `.home`, ect. ON MOD OBJECT")
            if openweb != "dep":
                logging.critical("DEPRECATION! DO NOT USE 'openweb' ARGUMENT, USE METHOD `.web_open()` ON MOD OBJECT")
                mod_object.web_open(web_save)
            if saveIcon != "dep":
                logging.critical("DEPRECATION! DO NOT USE 'saveIcon' ARGUMENT, USE METHOD `.save_icon()` ON MOD OBJECT")
                mod_object.save_icon()
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
