__author__ = "siznax"
__version__ = 2012
__credits__ = 'https://www.mediawiki.org/wiki/API:Main_page'

import os
import re
import sys
import wp_query
import json

class wp_info:

    def __init__(self):
        self.info = ''

    def infobox(self,txt,DEBUG=False):
        '''leak Infobox from Mediawiki API text output'''
        infobox = False
        braces = 0
        for line in txt:
            match = re.search(r'{{Infobox',line,flags=re.IGNORECASE)
            braces += len(re.findall(r'{{',line))
            braces -= len(re.findall(r'}}',line))
            if match:
                infobox = True
                line = re.sub(r'.*{{Infobox','{{Infobox',line)
            if infobox:
                if DEBUG: print "[%d] %s" % (braces,line.lstrip())
                self.info += line.lstrip() + "\n"
                if braces == 0:
                    break


def to_json(text):
    lines = text.split("\n")
    fields = []
    for line in lines:
        if line.startswith("|"):
            line = line.strip("|").strip()
            sep_index = line.index("=")
            key, value = line[:sep_index].strip(), line[sep_index + 1:].strip()
            fields.append({key: value})
        elif line.startswith("{{Infobox"):
            line = line.strip("{{Infobox").strip()
            fields.append({"infobox": line})

    return fields


def load(title):
    cache = "data/" + title
    if not os.path.exists(cache):
        text = wp_query.wp_query(sys.argv[1]).get()
        print "Saving to cache"
        f = open(cache, "w")
        f.write(text)
    else:
        with open(cache) as f:
            print "Loading from cache"
            text = f.read()

    i = wp_info()
    i.infobox(text.split("\n"))

    return i.info

# test cases TBD
#   Aerocar
#   GitHub
#   Heroku
#   Stack Overflow

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "%s title" % (os.path.basename(__file__))
        exit(1)
    if len(sys.argv) == 2:
        title = sys.argv[1]
        info = load(title)
        if not info:
            title = sys.argv[1].title()
            info = load(title)
            if not info:
                print "Can't find the title online or locally"

        print info,

        json_path = "data/" + title + ".json"
        with open(json_path, "w") as f:
            print "Writing to %s" % json_path
            f.write(json.dumps(to_json(info), indent=2))

        # with open(json_path) as f:
        #     print f.read()

        exit(0)
