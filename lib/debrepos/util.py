import os
import time
import random
import urllib2
import StringIO
import subprocess

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
    
def poll_process_for_complete_output(cmd):
    output = StringIO.StringIO()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        nextline = proc.stdout.readline()
        if nextline == '' and proc.poll() is not None:
            break
        output.write(nextline)
        output.flush()
    if proc.returncode:
        msg = "There was a problem with command: %s" % cmd
        raise RuntimeError, msg
    output.seek(0)
    return output



##################################
### hardlink dupes             ###
##################################

def find_dupes(args):
    fdupes = '/usr/bin/fdupes'
    dupelist = ''
    if len(args) == 1:
        arg = path(args[0])
        if arg.isfile():
            dupelist = file(arg).read()

    if not dupelist:
        cmd = [fdupes, '-r'] + args
        #print cmd
        output = poll_process_for_complete_output(cmd)
        return output.read()

def parse_dupelist(dupelist):
    dupes = []
    index = 0
    for line in dupelist.splitlines():
        if len(dupes) == index:
            dupes.append([])
        if line:
            dupes[index].append(line)
        else:
            index += 1
    return dupes

def chmod(directory, permarg, recursive=True):
    cmd = ['chmod']
    if recursive:
        cmd += ['-R']
    cmd += [permarg, directory]
    retval = subprocess.call(cmd)
    if retval:
        shcmd = ' '.join(cmd)
        raise RuntimeError , "%s returned %d" % (shcmd, retval)


def hardlink_dupes(directories):
    dupelist = find_dupes(directories)
    parsed = parse_dupelist(dupelist)
    for dupeset in parsed:
        orig = dupeset[0]
        dupes = dupeset[1:]
        for dupe in dupes:
            os.remove(dupe)
            os.link(orig, dupe)
        
