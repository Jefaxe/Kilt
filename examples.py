
# a bunch of random things with Kilt!
##


def lambd_update():
    import kilt
    # check lambdynamiclights version
    mod = kilt.search("light dy")[0]
    print("The latest version of {} is {}".format(mod.name, mod.version))


def caffein_install():
    import kilt
    # download sodium, lithium, and phosphor
    mods = kilt.search(search_array=["sodium", "lithium", "phosphor"])
    for i in mods:
        i.download()


def open_wiki():
    import kilt
    import webbrowser
    webbrowser.open(kilt._doc)


def specific_install():
    import kilt
    mod = kilt.search("lithium")[0]
    mod.download(specific_version="mc1.16.5-0.6.3")


def search_by_id():
    import kilt
    mod = kilt.search(mod_id="AZomiSrC")[0]
    print("{} is on version {}".format(mod.name, mod.version))



def search_array():
    import kilt
    mods = kilt.search(logging_level=0, search_array=["hydrogen", "galacticaft rewoven"])
    for mod in mods:
        print(mod.name)


def change_configs():
    from kilt import config
    config.global_level = 0
    import kilt
    kilt.search("zoom")


def facets_search():
    import kilt.labrinth as m
    mod = m.get(logging_level=0, mcversions=["1.14"], license_="MIT", server_side="unsupported")[0]
    mod.web_open("home")

facets_search()
