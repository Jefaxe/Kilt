import kilt

# a bunch of random things with Kilt!
##


def lambd_update():
    # check lambdynamiclights version
    mod = kilt.search("light dy")[0]
    print("The latest version of {} is {}".format(mod.name, mod.version))


def caffein_install():
    # download sodium, lithium, and phosphor
    mods = kilt.search(logging_level=20, search_array=["sodium", "lithium", "phosphor"], download_folder="mods")
    for i in mods:
        print(i.name)

