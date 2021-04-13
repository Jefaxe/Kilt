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
        with open("tests/correct.modlist.html") as file:
            correct = file.read()
        self.assertEqual(correct, res)

    def test_number_of_mods(self):
        try:
            n = labrinth.get_number_of_mods()
            success = "yay" if type(n) == int else "nay"
        except Exception as e:
            success = e
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

    def test_get_modlinks(self):
        mod = labrinth.search("fabric")[0]
        mod.web_open("home")
        mod.web_open("discord")
        mod.web_open("issues")
        mod.web_open("source")
        mod.web_open("donations")

    def test_version(self):
        from kilt import version
        print(version.__version__)

    def test_modloader(self):
        fabric_mod = labrinth.search("fabric")[0]  # the fabric API
        forge_mod = labrinth.search("oh")[0]  # Oh the Biomes You'll Go - forge only on modrinth
        self.assertEqual([True, True], [fabric_mod.is_fabric, forge_mod.is_forge], "There has been some error in the .isFabric and/or .isForge Mod methods")

    def test_author(self):
        author = labrinth.search("sodium")[0].author
        self.assertEqual("jellysquid3", author)
