import argparse
import webbrowser
import sys
import json
import urllib.request
import logging
import os

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def main():
    ###sets arguments
    parser = argparse.ArgumentParser(description='Searches modrinth')
    #meta
    parser.add_argument("-dir","--directory",help="set working directory. Defaults to ./kiltDATA",default="kiltDATA")
    #output
    parser.add_argument("-m","--modjson",help="Return ONLY the mod json, not the entire search json",action="store_true")
    parser.add_argument("-sj","--searchjson",help="Return ONLY the search json, the not specific mod json",action="store_true")
    parser.add_argument("-o","--output",help="Display the result in console.  Use --fileoutput to save to a file",action="store_true")
    parser.add_argument("-f","--outputfile",help="Send the output to a file")
    #filters
    parser.add_argument("-q","--search",help="Simply search modrith . -q stands for query",default="")
    parser.add_argument("-i","--index",help="How to filter the mods. (newest,updated,relevance,downloads)",default="newest")
    parser.add_argument("-p","--place",help="What location down the list to look for the mod?(default: 0 (top))",default=0,type=int)
    parser.add_argument("-l","--limit",help="Sets the number of mods that will be checked(default: 10)",default=10,type=int)
    #parser.add_argument("-cmc","--configureMC",help="Temparerily configure the minecraft version used for searching mods",default=config)
    #output events
    parser.add_argument("-D","--description",help="Saves the (short) description of the mod to generated/meta/descriptions.txt",action="store_true")
    # web events
    parser.add_argument("-H","--home",help="Opens the homepage of the mod",action="store_true")
    parser.add_argument("-is","--issues",help="Report bugs and suggest features here!",action="store_true")
    parser.add_argument("-s","--source",help="Visit the source code page of the mod",action="store_true")
    # downloads
    parser.add_argument("-d","--download",help="Downloads the requested mod",action="store_true")
    parser.add_argument("-b","--body",action="store_true",help="Downloads the description.md file for the requested mod. Only really useful when you have a .md vewier, like Markdown View")
    ##completes settting of arguments
    args = parser.parse_args()
    #if no arguments are passed, show the help screen
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
    args=parser.parse_args()
    if not os.path.exists(args.directory):
        os.makedirs(args.directory)
    os.chdir(args.directory)
    if not os.path.exists("generated/mods"):
        os.makedirs("generated/mods")
    if not os.path.exists("generated/meta"):
        os.makedirs("generated/meta")
    #sets up logging
    loggingFile="kilt.log"
    loggingFormat = '[%(filename)s][%(funcName)s/%(levelname)s] %(message)s'
    loggingLevel=logging.DEBUG
    logging.basicConfig(filename=loggingFile, level=loggingLevel,format=loggingFormat,filemode="w")

    ###
    #searching of mods
##
    if args.search!="":
        args.index="relevance"
    site="https://api.modrinth.com/api/v1/mod?query={whatmod}&limit={limit}&index={sort}&offset={place}"
    modSearch=site.format(whatmod=args.search,limit=args.limit,sort=args.index,place=args.place)
    logging.info("[ModrithAPI] Searching using: {search}".format(search=modSearch))
    modSearchJson=json.loads(urllib.request.urlopen(modSearch).read())
    modJsonFake = modSearchJson["hits"][0]
    modJsonURL = "https://api.modrinth.com/api/v1/mod/"+str(modJsonFake["mod_id"].replace("local-",""))
    modJson = json.loads(urllib.request.urlopen(modJsonURL).read())
    safeModJson = removekey(modJson,  "body")
    logging.debug("[ModrinthAPI] Requsted mod json(minus body): {json}".format(json=safeModJson))
    #logging.debug("[Modrinth]: {json}".format(json=modSearchJson))
    if args.place>=modSearchJson['total_hits']:
        logging.error("There are not THAT many in the search, set --limit in launch higher. Or that may be it all. NOTE THAT ARGS.PLACE WILL BE SET TO 0")
        args.place=0
        
    #output events
    if args.description:
        with open("generated/meta/descriptions.txt","a") as desc:
            desc.write(modJson["title"]+": "+modJson["description"]+"\n")
    #web events
    if args.home:
        webbrowser.open(modJsonFake["page_url"])
    if args.issues:
        webbrowser.open(modJson["issues_url"])
    if args.source:
        webbrowser.open(modJson["source_url"])

    #downloads
    if args.download:
        downloadLink = json.loads(urllib.request.urlopen("{json}/version".format(json=modJsonURL)).read())[0]["files"][0]["url"]
        logging.info("[Kilt] Downloading {mod} from {url}".format(mod=modJson["title"],url=downloadLink))
        download = urllib.request.urlopen(downloadLink)
        with open("generated/mods/{mod}".format(mod=downloadLink.rsplit("/",1)[-1]),"wb") as modsave:
                  modsave.write(download.read())
    if args.body:
        with open("generated/meta/{mod}".format(mod=modJson["title"]+".md"),"w") as modsave:
                  modsave.write(modJson["body"])
    valueToReturn= [modJson,modSearchJson]
    if args.modjson:
        valueToReturn=modJson
    if args.searchjson:
        valueToreturn=searchJson
    if args.output:
        print(valueToReturn)
    if args.outputfile is not None:
        with open(args.outputfile,"w") as file:
            for i in  [valueToReturn]:
                json.dump(i,file,indent=4)
    return valueToReturn
if __name__=="__main__":
    try:
        main()
    except (Exception,SystemExit) as e:
        if type(e)==SystemExit:
            print("The process crashed with exit code {code}".format(code=e))
        else:
            logging.error(str(e))
            print(e)
            print("The process ran into an error. The error can be found in kilt.log")
