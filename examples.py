import kilt
import webbrowser

# a bunch of random things with Kilt!
##


def lambd_update():
    # check lambdynamiclights version
    mod = kilt.search("light dy")[0]
    print("The latest version of {} is {}".format(mod.name, mod.version))


def caffein_install():
    # download sodium, lithium, and phosphor
    mods = kilt.search(search_array=["sodium", "lithium", "phosphor"])
    for i in mods:
        i.download()


def open_wiki():
    webbrowser.open(kilt._doc)


def specific_install():
    mod = kilt.search("lithium")[0]
    mod.download(specific_version="mc1.16.5-0.6.3")


def search_by_id():
    mod = kilt.search(mod_id="AZomiSrC")[0]
    print("{} is on version {}".format(mod.name, mod.version))


def works_but_depracted():
    # don't do this!
    kilt.search(download_folder=True)
    # don't do this!
    kilt.search(saveIcon=True)


def correct_way():
    # do this
    mod = kilt.search()[0]
    mod.download()
    # do this
    mod = kilt.search()[0]
    mod.save_icon()


def search_array():
    mods = kilt.search(search_array=["hydrogen", "galacticaft"])
    for mod in mods:
        print(mod.name)


search_array()