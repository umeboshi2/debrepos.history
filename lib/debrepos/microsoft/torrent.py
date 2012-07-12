import sys

import libtorrent as T

session = T.session()

def start_session():
    session.listen_on(6881, 6891)

def get_torrent_info(filename):
    return T.torrent_info(filename)

def make_add_torrent_data(info, save_path='./'):
    return dict(ti=info, save_path=save_path)

def add_torrent(filename):
    info = get_torrent_info(filename)
    handle = session.add_torrent(make_add_torrent_data(info))
    return handle

def is_torrent_downloaded(handle):
    return handle.is_seed()



    



sys.exit(0)


import libtorrent as lt
import time
import sys

ses = lt.session()
ses.listen_on(6881, 6891)

info = lt.torrent_info(sys.argv[1])
h = ses.add_torrent({'ti': info, 'save_path': './'})
print 'starting', h.name()

while (not h.is_seed()):
   s = h.status()

   state_str = ['queued', 'checking', 'downloading metadata', \
      'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
   print '\r%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % \
      (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
      s.num_peers, state_str[s.state]),
   sys.stdout.flush()

   time.sleep(1)

print h.name(), 'complete'
