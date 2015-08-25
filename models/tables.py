# coding: utf8
from datetime import datetime
import re
import unittest

# Format for wiki links.
RE_LINKS = re.compile('(<<)(.*?)(>>)')

db.define_table('pagetable' # Name 'page' is reserved unfortunately.
    # Complete!
    )


db.define_table('revision',
    # Complete!
    Field('body', 'text'), # This is the main content of a revision.
    )

db.define_table('testpage',
    # This table is used for testing only.  Don't use it in your code,
    # but feel free to look at how I use it. 
    Field('body', 'text'),
    )

def create_wiki_links(s):
    """This function replaces occurrences of '<<polar bear>>' in the 
    wikitext s with links to default/page/polar%20bear, so the name of the 
    page will be urlencoded and passed as argument 1."""
    def makelink(match):
        # The tile is what the user puts in
        title = match.group(2).strip()
        # The page, instead, is a normalized lowercase version.
        page = title.lower()
        return '[[%s %s]]' % (title, URL('default', 'index', args=[page]))
    return re.sub(RE_LINKS, makelink, s)

def represent_wiki(s):
    """Representation function for wiki pages.  This takes a string s
    containing markup language, and renders it in HTML, also transforming
    the <<page>> links to links to /default/index/page"""
    return MARKMIN(create_wiki_links(s))

def represent_content(v, r):
    """In case you need it: this is similar to represent_wiki, 
    but can be used in db.table.field.represent = represent_content"""
    return represent_wiki(v)

# We associate the wiki representation with the body of a revision.
db.revision.body.represent = represent_content
