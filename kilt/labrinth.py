import json
import logging
import os
import traceback
import urllib.error
import urllib.request
import webbrowser
from kilt import error, config, version
from PIL import Image

# sets up logging

logging.basicConfig(format="%(levelname)s: %(message)s [%(lineno)d]", level=config.global_level)


class Mod:
    def __init__(self, mod_struct):
        _localSite = version._site + "/"
        http_response = urllib.request.urlopen
        self.downloads = mod_struct["downloads"]
        self.sha1 = None
        self.discord = mod_struct["discord_url"]
        self.donations = mod_struct["donation_urls"]
        self.date_published = mod_struct["published"]
        self.last_updated = mod_struct["updated"]
        self.license = mod_struct["license"]  # this is a dict
        self.client = True if mod_struct["client_side"] in {"required", "optional"} else False
        self.server = True if mod_struct["server_side"] in {"required", "optional"} else False
        self.downloaded = False
        self.followers = mod_struct["followers"]
        self.categories = mod_struct["categories"]  # this is a list.
        self.name = mod_struct["title"]
        self.body = self.long_desc = mod_struct["body"]
        self.desc = self.description = mod_struct["description"]
        self.id = mod_struct["id"]
        self.home = "https://modrinth.com/mod/{}".format(mod_struct["slug"])
        self.source = mod_struct["source_url"]
        self.issues = mod_struct["issues_url"]
        try:
            mod_version_data = json.loads(
                http_response(_localSite + "{}/version".format(self.id)).read())[
                0]
            self.version = \
                mod_version_data["version_number"]
            self.loaders = \
                mod_version_data["loaders"]
            self.latest_mcversion = \
                mod_version_data["game_versions"][-1]
        except IndexError:  # there is no version
            self.version = None
            self.loaders = []
            self.latest_mcversion = None

        self.isFabric = self.is_fabric = True if "fabric" in self.loaders else False
        self.isForge = self.is_fabric = True if "forge" in self.loaders else False

    def save_icon(self, path=None, createTree=False):
        _localSite = version._site + "/"
        if path is None:
            path = "cache/" + self.name + ".png"
        icon_url = json.loads(urllib.request.urlopen(_localSite + "/mod/" + self.id).read())["icon_url"]
        if createTree:
            os.makedirs("".join(path.rsplit("/", 1)[:-1]))
        with open(path, "wb") as file:
            file.write(urllib.request.urlopen(icon_url).read())
        basewidth = 64
        img = Image.open(path)
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        img.save(path)

    def web_open(self, siteType="home", index_of_donation=0):
        if siteType == "home":
            webbrowser.open(self.home)
            return True
        elif siteType == "discord":
            webbrowser.open(self.discord)
            return True
        elif siteType == "donation":
            webbrowser.open(self.donations[index_of_donation])
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
        http_response = urllib.request.urlopen
        _localSite = version._site + "/"
        try:
            os.makedirs(download_folder, exist_ok=True)
            try:
                if specific_version is not None:
                    found = False
                    for i, index_value in json.loads(http_response(_localSite + "/mod/" + self.id + "/version").read()):
                        logging.debug(i["version_number"])
                        if i["version_number"] == specific_version:
                            mod_version = \
                                json.loads(http_response(_localSite + "/mod/" + self.id + "/version").read())[
                                    index_value][
                                    "files"][0]
                            found = True
                    if not found:
                        raise error.SpecificVersionNotFound(
                            "{} is not a version of '{}'".format(specific_version, self.name))
                else:
                    mod_version = json.loads(http_response(_localSite+ self.id + "/version").read())[0][
                        "files"][0]
                filename = mod_version["filename"]
                downloadLink = mod_version[
                    "url"]
                self.sha1 = mod_version["hashes"][
                    "sha1"]
            except IndexError:
                raise error.NoVersionFound("mod '{}' has no versions".format(self.name))
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
                with open(download_folder + "/{mod}".format(mod=downloadLink.rsplit("/", 1)[-1]).replace("%20",
                                                                                                         " "),
                          "wb") as modsave:
                    modsave.write(http_response(downloadLink).read())
            self.downloaded = True
        except urllib.error.HTTPError:
            logging.critical(
                "[Labrinth] COULD NOT DOWNLOAD MOD {} beacuse: {}".format(self.name,
                                                                          traceback.format_exc()))



def removekey(d, key):
    r = dict(d)
    del r[key]
    return r


def get_number_of_mods():
    number_of_mods = 0
    for i in range(1000000):
        mod_list = json.loads(urllib.request.urlopen(version._query.format("", 100, "newest", i * 100 + 1)).read())[
            "hits"]
        number_of_mods += len(mod_list)
        if len(mod_list) == 0:
            break
    return number_of_mods


def search(search="", mod_id=None, logging_level=config.global_level, modlist=config.modlist_enabled_by_default,
           index="relevance",
           offset=0,
           limit=10, saveDescriptionToFile=config.save_description_by_default, search_array=[],
           repeat=1):
    # create local variables for CPython optimized lookup
    http_response = urllib.request.urlopen
    _localSite = version._site + "/"
    MOD_OBJECTS = []
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    # make sure arguments are correct
    if index not in {"newest", "updated", "downloads", "relevance"}:
        raise error.InvalidArgument(
            "{} (index/sort) needs to be either 'newest', 'updated', 'downloads', or 'relevance'".format(index))
    if type(limit) is not int or limit not in list(range(0, 101)):
        raise error.InvalidArgument("{} (limit) is not in range 0, 100, or is not an integer.".format(limit))
    if type(offset) is not int or offset not in list(range(0, 101)):
        raise error.InvalidArgument("{} (offset) is not in range 0, 100, or it is not an integer".format(offset))
    if type(repeat) is not int or repeat <= 0:
        raise error.InvalidArgument("{} (repeat) is not an integer, or it is below 0.".format(repeat))
    ###
    # searching of mods
    ##
    if search != "":
        logging.info(
            "Using `search` completely disables `search_array. Also note that one element in search_array is faster than using search itself.")
        search_array = [search]
    search_array = list(map(lambda st: str.replace(st, " ", "%20"), search_array))
    logging.debug("Mods to search for: {}".format(", ".join(search_array)))
    if saveDescriptionToFile:  # anything but "False" or "None"
        if type(saveDescriptionToFile) is bool:
            saveDescriptionToFile = "descriptions.txt"
        with open(saveDescriptionToFile, "w") as file:
            file.write("Mod Descriptions\n")
    if modlist:  # anything but "False" or "None"
        if type(modlist) is bool:
            modlist = "modlist.html"
        with open(modlist, "w") as file:
            file.write("""<!DOCTYPE html>
                        <html>
                                <head>
                                        <title>Modlist</title>
                                </head>

                                <body>""")
    for offset in range(offset, repeat):
        if mod_id:
            try:
                mod_struct = json.loads(http_response(_localSite + mod_id).read())
            except urllib.error.HTTPError:
                raise error.InvalidModId("{} is not a valid modinth mod id".format(mod_id))
            mod_object = Mod(mod_struct)
            MOD_OBJECTS.append(mod_object)
        for this_search in search_array:
            logging.debug("Searching for {}".format(this_search))
            modSearch = version._query.format(this_search, limit, index, offset)
            logging.debug("Using {}".format(modSearch))
            modSearchJson = json.loads(http_response(modSearch).read())
            try:
                logging.debug("{} is the {} in search_array".format(this_search, search_array.index(this_search)))
                logging.debug(modSearchJson)
                mod_response = modSearchJson["hits"][0]
                logging.debug("{} is the mod_response of {}".format(mod_response, this_search))
            except IndexError:
                if offset == 0 and repeat == 1:
                    logging.info("There were no results for your search")
                    raise error.EndOfSearch("No results found for your query")
                elif offset == 0 and repeat != 1:
                    logging.info("You hit the end of your search!")
                    raise error.EndOfSearch(
                        "You attempted to access search result {} but {} was the max".format(offset + 1, offset))
                else:
                    logging.info(traceback.format_exc())
            mod_struct = json.loads(
                http_response(_localSite + str(mod_response["mod_id"].replace("local-", ""))).read())
            mod_struct_minus_body = removekey(mod_struct, "body")
            mod_object = Mod(mod_struct)
            MOD_OBJECTS.append(mod_object)
            logging.debug("[Kilt] Mod Objects are: {}".format(MOD_OBJECTS))
            logging.debug(
                "[Labrinth] Requested mod json(minus body): {json}".format(json=mod_struct_minus_body))
            # logging.debug("[Modrinth]: {json}".format(json=modSearchJson)
            # output events
            if saveDescriptionToFile:
                with open(saveDescriptionToFile, "a") as desc:
                    desc.write(mod_struct_minus_body["title"] + ": " + mod_struct_minus_body["description"] + "\n")

            if modlist:
                with open(modlist, "a") as file:
                    file.write(
                        "<image src={} width=64 height=64 alt={}></image><a href={}>{} (by {})</a><p></p>".format(
                            mod_struct_minus_body["icon_url"],
                            mod_struct_minus_body["title"],
                            mod_response["page_url"],
                            mod_struct_minus_body["title"],
                            mod_response["author"]))
            # deprecation warnings!

    if modlist:
        with open(modlist, "a") as file:
            file.write(""" </body>
</html>""")
    return MOD_OBJECTS


if __name__ == "__main__":
    print("Don't run this!")
