import time
import traceback
import unittest
import os
import json

os.chdir("..")
from kilt import labrinth


class UnitTestsForKilt(unittest.TestCase):
    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            return exc_list[-1][1]

    def setUp(self):
        self._started_at = time.time()

    def tearDown(self):
        result = self.defaultTestResult()  # These two methods have no side effects
        self._feedErrorsToResult(result, self._outcome.errors)
        error = self.list2reason(result.errors)
        failure = self.list2reason(result.failures)
        okay = not error and not failure
        if okay:
            elapsed = time.time() - self._started_at
            print("{} completed in {} seconds".format(self.id(), elapsed))
            with open("tests/test-results.json") as res:
                results = json.load(res)
            testName = self.id().replace("unit.UnitTestsForKilt.test_", "")
            try:
                results[testName].append(elapsed)
            except KeyError:
                results.update({testName: [elapsed]})
            with open("tests/test-results.json", "w") as res:
                json.dump(results, res, indent=4)

            meanResult = sum(results[testName]) / len(results[testName])
            with open("tests/mean.json") as fresh:
                structure = json.load(fresh)
            structure[testName] = meanResult
            with open("tests/mean.json", "w") as m:
                json.dump(structure, m, indent=4)

    def test_download(self):
        mod = labrinth.search("zoom")[0]
        mod.download()
        self.assertEqual(True, mod.downloaded)

    def test_download_specific(self):
        mod = labrinth.search("Adorn")[0]
        mod.download(specific_version="1.13.0")
        self.assertEqual("1.13.0", mod.version)

    def test_id_search(self):
        try:
            mod = labrinth.search(mod_id="AZomiSrC")[0]
            if mod.name == "Hydrogen":
                success = "yay"
            else:
                success = "nay"
        except Exception:
            success = traceback.format_exc()
        self.assertEqual("yay", success)

    def test_modlist(self):
        labrinth.search(modlist=True, search_array=["p", "lithium"])
        with open("modlist.html") as file:
            res = file.read()
        with open("tests/correct/modlist.html") as file:
            correct = file.read()
        self.assertEqual(correct, res)

    def test_number_of_mods(self):
        try:
            n = labrinth.get_number_of_mods()
            print(n)
            success = "yay" if type(n) == int else "nay"
        except Exception as e:
            success = traceback.format_exc()
        self.assertEqual("yay", success)

    def test_search(self):
        mod = labrinth.search(search="lithium")[0]
        # print(mod.name)
        self.assertEqual("Lithium", mod.name)

    def test_search_array(self):
        mods = labrinth.search(search_array=["lithium", "sodium", "TwoFA", "galaciraft"])
        self.assertEqual(["Lithium", "Sodium", "TwoFA", "Galacticraft: Rewoven"], [item.name for item in mods])

    def test_single_search_array(self):
        mod = labrinth.search(search_array=["lithium"])[0]
        self.assertEqual("Lithium", mod.name)

    def test_version(self):
        from kilt import version
        version.update_log(outputfile="tests/version.txt")

    def test_facets_search(self):
        mod = labrinth.get(mcversions=["1.14"], license_="MIT", server_side="unsupported")[0]
        self.assertEqual("NBT Tooltip", mod.name)
    def test_modloader(self):
        fabric_mod = labrinth.search("fabric")[0]  # the fabric API
        forge_mod = labrinth.search("oh")[0]  # Oh the Biomes You'll Go - forge only on modrinth
        self.assertEqual([True, True], [fabric_mod.is_fabric, forge_mod.is_forge],
                         "There has been some error in the .isFabric and/or .isForge Mod methods")

    def test_author(self):
        author = labrinth.get("sodium")[0].author
        self.assertEqual("jellysquid3", author)

    def test_search_spec_version(self):
        mod = labrinth.get("Aethor", mod_versions=["b1.0"])[0]
        mod.download()

    def test_download_icon(self):
        mod = labrinth.get("hydrogen")[0]
        mod.save_icon()
        with open("icons/" + mod.name + ".png", "rb") as fp:
            res = fp.read()
        with open("tests/correct/" + mod.name + ".png", "rb") as fp:
            correct = fp.read()
        self.assertEqual(correct, res)

    def test_meilisearch(self):
        mod = labrinth.get(categories_meilisearch="categories='forge' AND NOT categories='fabric'")[0]
        self.assertEqual("Oh The Biomes You'll Go", mod.name)

    def test_no_search(self):
        mods = labrinth.get()
        self.assertGreaterEqual(len(mods), 1)

    def test_mcversion_check(self):
        mod = labrinth.get("reforged", mcversions=["1.9.4"])
    def test_create_custom_mod_object(self):
        mod_struct = {"id": "eaqEFY9F", "slug": "wiidudes-custom-origins", "team": "FuRASOII",
                      "title": "WiiDude's Custom Origins", "description": "An addon mod for origins.",
                      "body": "# Custom Origin Info\nFox:<br>\n[+] Runs faster than a normal player<br>\n[+] Gets a health boost from eating sweet berries and chicken<br>\n[+] Jumps higher<br>\n[-] Wolves do double damage<br>\n[-] A bit shorter than players\n\n### Changelog\nV1.0.0 Added a fox origin, initial commit.\n### Things to know:\nThis is heavily based off of the extra origins mod.<br>\nTHIS WILL NEVER BE ON FORGE, DONT ASK<br>\nPehkui Version 1.9.0+ required or you will experience a crash on world loading.<br>\nOrigins mod 0.6+ or you will get a crash when using the fox origin. <br>",
                      "body_url": None, "published": "2021-03-14T03:53:18.940174Z",
                      "updated": "2021-03-23T22:12:07.582828Z", "status": "approved",
                      "license": {"id": "lgpl-3", "name": "GNU Lesser General Public License v3",
                                  "url": "https://cdn.modrinth.com/licenses/lgpl-3.txt"}, "client_side": "required",
                      "server_side": "required", "downloads": 5, "followers": 1,
                      "categories": ["adventure", "misc", "utility"], "versions": ["hlRYfpTi", "P5MZvSIZ", "QuCPZjSa"],
                      "icon_url": "https://cdn.modrinth.com/data/eaqEFY9F/icon.png",
                      "issues_url": "https://github.com/Developer-Doge/Fox-Origin/issues",
                      "source_url": "https://github.com/Developer-Doge/Fox-Origin",
                      "wiki_url": "https://github.com/Developer-Doge/Fox-Origin/wiki", "discord_url": None,
                      "donation_urls": []}

        custom_mod = labrinth.Mod(mod_struct)
