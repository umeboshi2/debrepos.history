import os, sys
import urllib2



from debrepos.microsoft.oembios import get_oembios_urls
from debrepos.microsoft.oembios import split_oembios_urls



import os, sys
import operator
import time

from debrepos.microsoft.torrent import session, start_session
from debrepos.microsoft.torrent import add_torrent
from debrepos.microsoft.driverpacks import parse_rss_feed
from debrepos.microsoft.driverpacks import get_driverpacks, get_torrents

from debrepos.microsoft.driverpacks import DriverPack

def get_torrent_file(url, targetdir):
    basename = os.path.basename(url)
    outfilename = os.path.join(targetdir, basename)
    res = urllib2.urlopen(url)
    content = res.read()
    outfile = file(outfilename, 'w')
    outfile.write(content)
    outfile.close()

def get_torrents(urls, targetdir):
    for url in urls:
        get_torrent_file(url, targetdir)
        



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
    urls = get_oembios_urls(indexfile=indexfile)
    xf = split_oembios_urls(urls)

    torrent_dir = 'torrents'

    here = os.getcwd()
    if not os.path.isdir(torrent_dir):
        os.mkdir(torrent_dir)
    get_torrents(urls, torrent_dir)



torrents = os.listdir('torrents')

start_session()

handles = []
for torrent in torrents:
    filename = os.path.join('torrents', torrent)
    handle = add_torrent(filename)
    handles.append(handle)

all_seeded = False
while not all_seeded:
    seeded = [h.is_seed() for h in handles]
    all_seeded = reduce(operator.and_, seeded)
    for h in handles:
        if not h.is_seed():
            print "downloading", h.name()
    print 50*'='
    downloading = len([h for h in handles if not h.is_seed()])
    print "Downloading %d torrents" % downloading
    print 50*'='
    time.sleep(10)
    
