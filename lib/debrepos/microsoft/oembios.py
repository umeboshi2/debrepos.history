import os, sys
import urllib2
from urllib2 import HTTPError
from httplib import IncompleteRead

import feedparser

from debrepos.path import path

from debrepos.util import handle_link

DRIVERPACKS_LATEST_FEED = 'http://driverpacks.net/driverpacks/latest/feed'

OEMBIOS_URL = 'http://www.oembios.net'

# indexfile is file object
def get_oembios_links(indexfile=None):
    if indexfile is None:
        indexfile = urllib2.urlopen(OEMBIOS_URL)
    links = []
    for line in indexfile:
        if 'HREF' in line and '/filesets/' in line:
            link = line.split('"')[1]
            links.append(link)
    return links

def get_oembios_urls(indexfile=None):
    links = get_oembios_links(indexfile=indexfile)
    return ['%s%s' % (OEMBIOS_URL, l) for l in links]

def split_oembios_urls(urls):
    xfertype = dict(torrent=[], rar=[])
    for url in urls:
        if url.endswith('.torrent'):
            xfertype['torrent'].append(url)
        elif url.endswith('.rar'):
            xfertype['rar'].append(url)
        else:
            raise RuntimeError , "Unhandled url: %s" % url
    return xfertype

        

if __name__ == '__main__':
    oembios_index_filename = 'oembios.index.html'
    if os.path.isfile(oembios_index_filename):
        content = file(oembios_index_filename).read()
    else:
        r = urllib2.urlopen(OEMBIOS_URL)
        content = r.read()
        outfile = file(oembios_index_filename, 'w')
        outfile.write(content)
        outfile.close()

    indexfile = file(oembios_index_filename)
    links = get_oembios_links(indexfile=indexfile)
    indexfile.seek(0)
    urls = get_oembios_urls(indexfile=indexfile)
    xf = split_oembios_urls(urls)
    
    
    
