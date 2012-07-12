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



    



