import json
import logging
import os
import traceback
import urllib.error
import urllib.request
import webbrowser
from kilt import error, config, version
from PIL import Image

labrinth_mod = "https://api.modrinth.com/api/v1/mod"

kilt_doc = "https://github.com/Jefaxe/Kilt/wiki"

labrinth_doc = "https://github.com/modrinth/labrinth/wiki/API-Documentation"

# sets up logging
logging.basicConfig(format="%(levelname)s: %(message)s [%(lineno)d]", level=config.global_level)
logger = logging.getLogger()


class Mod(object):
    def define_page(self, mod_struct):
        self.name = mod_struct["title"]
        self.body = self.long_desc = mod_struct["body"]
        self.desc = self.description = mod_struct["description"]
        self.id = mod_struct["id"]

    def define_stats(self, mod_struct, author="unknown"):
        self.date_published = mod_struct["published"]
        self.last_updated = mod_struct["updated"]
        self.author = author
        self.author_url = "https://modrinth.com/user/" + self.author
        self.icon_link = mod_struct["icon_url"]
        self.license = mod_struct["license"]  # this is a dict
        self.downloads = mod_struct["downloads"]
        self.followers = mod_struct["followers"]
        self.discord = mod_struct["discord_url"]
        self.donations = mod_struct["donation_urls"]
        self.home = "https://modrinth.com/mod/{}".format(mod_struct["slug"])
        self.source = mod_struct["source_url"]
        self.issues = mod_struct["issues_url"]

    def define_categories(self, mod_struct):
        self.categories = mod_struct["categories"]  # this is a list.
        self.mc_versions = mod_struct["versions"]  # list again
        self.client_req = True if mod_struct["client_side"] == "required" else False
        self.server_req = True if mod_struct["server_side"] == "required" else False
        self.client_opt = True if mod_struct["client_side"] == "optional" else False
        self.server_opt = True if mod_struct["server_side"] == "optional" else False
        self.plugin = True if self.server_req and not self.client_req else False
        self.client_only = True if self.client_req and not self.server_req else False
        self.content_mod = True if self.client_req and self.server_req else False

    def init_version(self, mod_struct, spec_version, mcversion=None):
        _localSite = labrinth_mod + "/"
        http_response = urllib.request.urlopen
        try:
            mod_version_data = json.loads(
                http_response(_localSite + "{}/version".format(self.id)).read())[
                0]
            if spec_version is not None:
                found = False
                versions = json.loads(http_response(_localSite + self.id + "/version").read())
                for index_value in versions:
                    if index_value["version_number"] == spec_version:
                        mod_version_data = \
                            json.loads(http_response(_localSite + self.id + "/version").read())[
                                versions.index(index_value)]
                        found = True
                if not found:
                    raise error.SpecificVersionNotFound(
                        "{} is not a version of '{}'".format(version, self.name))
            self.version = mod_version_data["version_number"]
            self.loaders = \
                mod_version_data["loaders"]
            self.latest_mcversion = \
                mod_version_data["game_versions"][-1] if mcversion is None else mcversion
        except IndexError:  # there is no version
            self.version = None
            self.loaders = []
            self.latest_mcversion = None
        self.isFabric = self.is_fabric = True if "fabric" in self.loaders else False
        self.isForge = self.is_forge = True if "forge" in self.loaders else False

    def __init__(self, mod_struct, author="unknown", spec_version=None, mcversion=None):
        self.define_page(mod_struct)
        self.define_stats(mod_struct, author=author)
        self.init_version(mod_struct, spec_version=spec_version, mcversion=mcversion)
        self.define_categories(mod_struct)
        self.sha1 = None
        self.downloaded = False

    def save_icon(self, path=None, createTree=True, resolution=512):
        if path is None:
            path = "icons/" + self.name + ".png"
        if createTree:
            os.makedirs("".join(path.rsplit("/", 1)[:-1]), exist_ok=True)
        with open(path, "wb") as file:
            file.write(urllib.request.urlopen(self.icon_link).read())
        if resolution != 512:
            img = Image.open(path)
            wpercent = (resolution / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((resolution, hsize), Image.ANTIALIAS)
            img.save(path)

    def web_open(self, siteType="home", index_of_donation=0, open_new_tab=False):
        new_window = 1 if open_new_tab else 0
        if siteType == "home":
            webbrowser.open(self.home, new=new_window)
            return True
        elif siteType == "discord":
            webbrowser.open(self.discord, new=new_window)
            return True
        elif siteType == "donation":
            webbrowser.open(self.donations[index_of_donation], new=new_window)
        elif siteType == "source":
            webbrowser.open(self.source, new=new_window)
            return True
        elif siteType == "issues":
            webbrowser.open(self.issues, new=new_window)
            return True
        else:
            return False

    def download(self, download_folder="mods", specific_version="will default to self.version"):
        specific_version = self.version if specific_version == "will default to self.version" else specific_version
        # downloads
        http_response = urllib.request.urlopen
        _localSite = labrinth_mod + "/"
        try:
            os.makedirs(download_folder, exist_ok=True)
            try:
                if specific_version is not None:
                    found = False
                    versions = json.loads(http_response(_localSite + self.id + "/version").read())
                    for index_value in versions:
                        if index_value["version_number"] == specific_version:
                            mod_version = \
                                json.loads(http_response(_localSite + self.id + "/version").read())[
                                    versions.index(index_value)][
                                    "files"][0]
                            found = True
                            self.version = specific_version
                    if not found:
                        raise error.SpecificVersionNotFound(
                            "{} is not a version of '{}'".format(specific_version, self.name))
                else:
                    mod_version = json.loads(http_response(_localSite + self.id + "/version").read())[0][
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
                logging.debug(
                    "[Kilt] Downloading {mod} from {url}".format(mod=self.name,
                                                                 url=downloadLink))
                with open(download_folder + "/{mod}".format(mod=downloadLink.rsplit("/", 1)[-1]).replace("%20",
                                                                                                         " "),
                          "wb") as modsave:
                    modsave.write(http_response(downloadLink).read())
            self.downloaded = True
        except urllib.error.HTTPError:
            logging.critical(
                "[Labrinth] COULD NOT DOWNLOAD MOD {} because: {}".format(self.name,
                                                                          traceback.format_exc()))
        return self.downloaded


def removekey(d, key):
    r = dict(d)
    del r[key]
    return r


def get_number_of_mods():
    return json.loads(urllib.request.urlopen(labrinth_mod + "?").read())[
        "total_hits"]


# alias
number_of_mods = get_number_of_mods


def get(search="", mod_id=None, logging_level=config.global_level, modlist=config.modlist_default,
        index="relevance",
        offset=0,
        limit=10, saveDescriptionToFile=config.description_default, search_array=None,
        repeat=1, mod_versions=None, categories_meilisearch="", license_=None, mcversions=None, client_side=None,
        server_side=None):
    # note mod_versions MUST be indexed 1-1 with search_array!!
    # create local variables for CPython optimized lookup
    if mod_versions is None:
        mod_versions = []
    if search_array is None:
        search_array = []
    if mcversions is None:
        mcversions = []
    http_response = urllib.request.urlopen
    _localSite = labrinth_mod + "/"
    MOD_OBJECTS = []
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    # make sure arguments are correct
    side_dict = {"True": "required",
                 "False": "unsupported",
                 "required": "required",
                 "unsupported": "unsupported",
                 "None": None}
    client_side = side_dict[str(client_side)]
    server_side = side_dict[str(server_side)]
    logging.debug("Server side: {} | Client Side: {}".format(server_side, client_side))
    if index not in {"newest", "updated", "downloads", "relevance"}:
        raise error.InvalidArgument(
            "{} (index/sort) needs to be either 'newest', 'updated', 'downloads', or 'relevance'".format(index))
    if type(limit) is not int or limit not in list(range(0, 101)):
        raise error.InvalidArgument("{} (limit) is not in range 0, 100, or is not an integer.".format(limit))
    if type(offset) is not int or offset not in list(range(0, 101)):
        raise error.InvalidArgument("{} (offset) is not in range 0, 100, or it is not an integer".format(offset))
    if type(repeat) is not int or repeat <= 0:
        raise error.InvalidArgument("{} (repeat) is not an integer, or it is below 0.".format(repeat))
    if client_side not in {"required", "unsupported", None}:
        raise error.InvalidArgument("{} (client_side) needs to be either `required` or `unsupported`")
    if server_side not in {"required", "unsupported", None}:
        raise error.InvalidArgument("{} (server_side) needs to be either `required` or `unsupported`")
    # patch arguments
    if search != "":
        logging.info(
            "Using `search` completely disables `search_array. Also note that one element in search_array is faster than using search itself.")
        search_array = [search]
    search_array = list(map(lambda st: str.replace(st, " ", "%20"), search_array))
    if not search_array:
        search_array = [""]
    categories_meilisearch = categories_meilisearch.replace(" ", "%20")

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
        mod_ver = mod_versions[offset] if mod_versions else None
        if mod_id:
            try:
                mod_struct = json.loads(http_response(_localSite + mod_id).read())
            except urllib.error.HTTPError:
                raise error.InvalidModId("{} is not a valid modrinth mod id".format(mod_id))
            mod_object = Mod(mod_struct, spec_version=mod_ver, mcversion=mcversions[0] if mcversions else None)
            MOD_OBJECTS.append(mod_object)
        for this_search in search_array:
            logging.debug("Searching for {}".format(this_search))
            facets_bool = False
            facets_string = "["
            if license_ is not None:
                facets_string += '["license:{}"]'.format(license_) + ","
                facets_bool = True
            if mcversions:
                for mcv in mcversions:
                    facets_string += '["versions:{}"]'.format(mcv) + ","
                facets_bool = True
            if client_side is not None:
                facets_string += '["client_side:{}"]'.format(client_side)
                facets_bool = True
            if server_side is not None:
                facets_string += '["server_side:{}"]"'.format(server_side)
                facets_bool = True
            if facets_bool:
                logging.debug("Fancy! Using facets i see!")
                facets_string = facets_string[:-1]
                facets_string += "]"
                facets = urllib.parse.quote(facets_string)
                modSearch = labrinth_mod + "?query={}&limit={}&index={}&offset={}&filters={}&facets={f}".format(
                    this_search, limit, index, offset, categories_meilisearch, f=facets)
            else:
                modSearch = labrinth_mod + "?query={}&limit={}&index={}&offset={}&filters={}".format(
                    this_search, limit, index, offset, categories_meilisearch)
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
            mod_ver = mod_versions[search_array.index(this_search)] if len(mod_versions) == len(search_array) else None
            mod_object = Mod(mod_struct, author=mod_response["author"], spec_version=mod_ver)
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


# alias
search = get

if __name__ == "__main__":
    print("don't run this")
