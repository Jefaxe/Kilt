import logging
import kilt


def main():
    number_of_mods = kilt.get_number_of_mods()
    logging.info("Downloading all the mods on modrinth.. This will take a very long time, check kilt.log for details..")
    kilt.search(repeat=number_of_mods, limit=100, download_folder=True, crash=False, modlist="modlist.html")
    logging.info("Downloaded {} mods from modrinth using labrinth and kilt".format(number_of_mods))


if __name__ == "__main__":
    main()
