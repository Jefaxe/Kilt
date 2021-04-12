import time
import traceback
import unittest
import os
import json
os.chdir("..")



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
        from kilt import labrinth
        try:
            mod = labrinth.search("zoom")[0]
            mod.download()
            success = "yay"
        except Exception:
            success = traceback.format_exc()
        self.assertEqual("yay", success)

    def test_id_search(self):
        from kilt import labrinth
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
        from kilt import labrinth
        labrinth.search(modlist=True, search_array=["p", "lithium"])
        with open("modlist.html") as file:
            res = file.read()
        with open("tests/correct.modlist.html") as file:
            correct = file.read()
        self.assertEqual(correct, res)

    def test_number_of_mods(self):
        from kilt import labrinth
        try:
            labrinth.get_number_of_mods()
            success = "yay"
        except Exception as e:
            success = e
        self.assertEqual("yay", success)

    def test_search(self):
        from kilt import labrinth
        mod = labrinth.search(search="lithium")[0]
        # print(mod.name)
        self.assertEqual("Lithium", mod.name)

    def test_search_array(self):
        from kilt import labrinth
        mods = labrinth.search(search_array=["lithium", "sodium", "TwoFA", "galaciraft"])
        self.assertEqual(["Lithium", "Sodium", "TwoFA", "Galacticraft: Rewoven"], [item.name for item in mods])

    def test_single_search_array(self):
        from kilt import labrinth
        mod = labrinth.search(search_array=["lithium"])[0]
        self.assertEqual("Lithium", mod.name)

    def test_override_logging(self):
        # this test MUST be done in isolation to work, and MUST be checked manually (for now?)
        from kilt import config
        config.global_level = 0  # NOTSET
        from kilt import labrinth
        labrinth.search("zoom")
