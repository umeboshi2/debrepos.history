import os, sys
import urllib2
from urllib2 import HTTPError
from httplib import IncompleteRead

import feedparser

from useless.base.path import path

from debrepos.util import handle_link

DRIVERPACKS_LATEST_FEED = 'http://driverpacks.net/driverpacks/latest/feed'




class DriverPack(object):
    def __init__(self, title, link):
        self.title = title
        self.link = link
        self._parse_link()
        
    def _parse_link(self):
        link = self.link
        for attr in ['version', 'packname', 'arch', 'winver']:
            link, basename = os.path.split(link)
            setattr(self, attr, basename)

    def download_link(self):
        return os.path.join(self.link, 'download/torrent')

    def get_torrent_info(self):
        url = self.download_link()
        try:
            return handle_link(url)
        except HTTPError:
            return dict()
        
    def get_torrent(self):
        info = self.get_torrent_info()
        if not info:
            print "Bad torrent", self.download_link()
            return
        filename = info['filename']
        if not os.path.isfile(filename):
            print "Downloading", filename
            output = file(filename, 'w')
            content = info['fileobj'].read()
            output.write(content)
            output.close()
        else:
            print "torrent", self.packname, self.winver, self.arch, 'exists.'
            
            
def get_driverpacks(parser):
    driverpacks = []
    for entry in parser.entries:
        dp = DriverPack(entry.title, entry.link)
        driverpacks.append(dp)
    return driverpacks

def get_torrents(driverpacks):
    for dp in driverpacks:
        dp.get_torrent()
        

if __name__ == '__main__':
    import pickle
    filename = path('feed.pickle')
    if filename.isfile():
        parser = pickle.load(file(filename))
    else:
        print 'downloading feed...'
        parser = feedparser.parse(DRIVERPACKS_LATEST_FEED)
        feed_dump = file(filename, 'w')
        pickle.dump(feed, feed_dump)
        feed_dump.close()
    p = parser
    
    d = get_driverpacks(p)
    get_torrents(d)
    
    
