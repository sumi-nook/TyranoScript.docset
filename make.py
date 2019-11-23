#!/usr/bin/env python3

import argparse
import os
import re
import sqlite3
import sys

from bs4 import BeautifulSoup
from bs4 import NavigableString
from bs4 import Comment
from bs4 import Tag

DOCUMENT_HEADER = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<style>
ul.area_group {
  display: none;
}
</style>
</head>
<body>
"""
DOCUMENT_FOOTER = """
</body>
</html>
"""


def main():
    conn = sqlite3.connect("TyranoScript.docset/Contents/Resources/docSet.dsidx")
    cur = conn.cursor()

    try:
        cur.execute("DROP TABLE searchIndex;")
    except:
        pass

    cur.execute("CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);")
    cur.execute("CREATE UNIQUE INDEX anchor ON searchIndex(name, type, path);")

    docpath = "src/tyrano.jp/tag/index.html"

    found = False
    bs = BeautifulSoup(open(docpath).read())
    for item in bs.find_all("div", {"class": "container"}):
        comments = item.find_all(string=lambda x: isinstance(x, Comment))
        if not comments:
            continue
        for comment in comments:
            if "この下に生成されたHTMLを入れる" in comment:
                found = True
                break
        if found:
            break
    with open("TyranoScript.docset/Contents/Resources/Documents/index.html", "w") as fp:
        fp.write(DOCUMENT_HEADER)
        fp.write(item.prettify())
        fp.write(DOCUMENT_FOOTER)

    for tag in item.find_all("a", {"href": re.compile(".+")}):
        name = tag.text.strip()
        if not name:
            continue
        path = "index.html" + tag.attrs["href"].strip()
        cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)", (name, "func", path))
        print("name:", name, ", path:", path)

    conn.commit()
    conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())

