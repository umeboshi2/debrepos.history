import os
import time
import random
import urllib2

class FileExistsError(Exception):
    pass

class BadDownloadError(Exception):
    pass

# FIXME:  need to actually use arguments
# this function is hardcoded
def random_wait(minimum=5, maximum=15, msg=''):
    #seconds = random.randint(minimum, maximum)
    seconds = random.random()*2 + 1
    if msg:
        template_data = dict(seconds=seconds)
        msg = msg % template_data
        print msg
    time.sleep(seconds)



def handle_link(uri):
    data = dict()
    attachment_marker = 'attachment;'
    filename_marker = 'filename='
    disposition_key = 'content-disposition'
    length_key = 'content-length'
    f = urllib2.urlopen(uri)
    info = f.info()
    data['info'] = info
    data['fileobj'] = f
    # presume no attachment first
    data['attachment'] = False
    if disposition_key in info:
        disposition = info[disposition_key]
        if disposition.startswith(attachment_marker):
            data['attachment'] = True
            fragment = disposition.split(attachment_marker)[1]
            filename = fragment.split(filename_marker)[1]
            length = int(info[length_key])
            data['filename'] = filename
            data['length'] = length
    return data

# here fileobj is addinfourl object from urlopen()
# filename is name to save file retrieved from fileobj
# length is the size that the fileobj is supposed to be
# if overwrite is set to False, a RuntimeError will be
# raised
def download_uri(fileobj, filename, length, overwrite=False):
    if not overwrite and os.path.exists(filename):
        raise FileExistsError , "File already exists: %s" % filename
    output = file(filename, 'w')
    block = fileobj.read(1024)
    while block:
        output.write(block)
        block = fileobj.read(1024)
    output.close()
    if os.path.getsize(filename) != length:
        raise BadDownloadError , "There was a problem downloading this url"
    
