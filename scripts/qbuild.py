import os, sys
import subprocess

import apt
from useless.base.path import path


class ChangesNotFoundError(Exception):
    pass


def cleanup(pkgname):
    here = path.getcwd()
    ls = [f.relpath() for f in here.listdir()]
    marker = '%s-' % pkgname
    dirtyfiles = [f for f in ls if f.startswith(marker) and f.isfile()]
    for fname in dirtyfiles:
        print "Removing", fname
        os.remove(fname)
    dirtydirs = [f for f in ls if f.startswith(marker) and f.isdir()]
    for dname in dirtydirs:
        print "Removing", dname
        cmd = ['rm', '-fr', dname]
        subprocess.check_call(cmd)
        
    
    

def get_source(pkgname):
    cmd = ['apt-get', 'source', pkgname]
    subprocess.check_call(cmd)

def dget(dsc_url):
    cmd = ['dget', '-xu', dsc_url]
    subprocess.check_call(cmd)

def get_dirname(pkgname):
    here = path.getcwd()
    ls = [f.relpath() for f in here.listdir()]
    marker = '%s-' % pkgname
    pkgdirs = [f for f in ls if f.startswith(marker) and f.isdir()]
    if not pkgdirs or len(pkgdirs) > 1:
        msg = "unable to find extracted directory for %s" % pkgname
        raise RuntimeError , msg
    return pkgdirs.pop()

def get_dscfile(pkgname):
    here = path.getcwd()
    ls = [f.relpath() for f in here.listdir()]
    filtered = [f for f in ls if f.startswith(pkgname) and f.endswith('.dsc')]
    #print "FILTERED", filtered
    if len(filtered) == 1:
        return filtered[0]
    if len(filtered) != 2:
        raise RuntimeError , "something bad happened, too many .dsc files"
    versions = [f.split('_')[1] for f in filtered]
    versions = [f.split('.dsc')[0] for f in versions]
    compare = apt.VersionCompare(*versions)
    if not compare:
        raise RuntimeError , "There has been no update in the changelog"
    if compare == 1:
        return filtered[0]
    elif compare == -1:
        return filtered[1]
    else:
        raise RuntimeError , "There has been an unknown problem"

def build_source_package(dirname):
    here = path.getcwd()
    os.chdir(dirname)
    cmd = ['dch', 'local build']
    subprocess.check_call(cmd)
    cmd = ['dpkg-buildpackage', '-S', '-sa']
    retcode = subprocess.call(cmd)
    if retcode not in [0, 1]:
        raise RuntimeError , "dpkg-buildpackage returned %d" % retcode
    os.chdir(here)
    
def cowpoke(dscfile, binonly=False):
    if binonly:
        cmd = ['cowpoke', '--arch=i386', '--create',
               "--dpkg-opts='-B'", dscfile]
    else:
        cmd = ['cowpoke', dscfile]
    if not binonly:
        subprocess.check_call(cmd)
    else:
        retcode = subprocess.call(cmd)
        if retcode not in [0,1]:
            raise RuntimeError , "error building %s" % dscfile
        return retcode
    
def get_result(arch='amd64'):
    cmd = ['rsync', '-av',
           'root@builder:/var/cache/pbuilder/%s/squeeze/result/' % arch,
           'result.%s/' % arch]
    subprocess.check_call(cmd)

def find_result_changes(pkgname, arch='amd64'):
    resultdir = path('result.%s' % arch)
    files = resultdir.listdir()
    all_changes = [f for f in files if f.endswith('_%s.changes' % arch)]
    #print "ALL_CHANGES", all_changes
    pkg_changes = [f for f in all_changes \
                       if f.basename().startswith('%s_' % pkgname)]
    if len(pkg_changes) != 1:
        msg = "problem finding changes file -> %s" % pkg_changes
        raise ChangesNotFoundError , msg
    return pkg_changes[0]

def dput(changes):
    cmd = ['dput', 'cypress', changes]
    subprocess.check_call(cmd)
    
    
    
    
    
def main(pkgname):
    # build for amd64 first
    cleanup(pkgname)
    get_source(pkgname)
    dirname = get_dirname(pkgname)
    build_source_package(dirname)
    dscfile = get_dscfile(pkgname)
    cowpoke(dscfile)
    get_result()
    changes = find_result_changes(pkgname)
    dput(changes)
    amd64_changes = changes
    # build for i386
    i386_changes = None
    retcode = cowpoke(dscfile, binonly=True)
    get_result(arch='i386')
    try:
        changes = find_result_changes(pkgname, arch='i386')
        dput(changes)
    except ChangesNotFoundError:
        helper_file = path('cowssh_it')
        if helper_file.isfile():
            helper_file.remove()
        print "There doesn't seem to be a binary for i386"
        print "Please doublecheck"
    print "Finished Building %s" % pkgname
    
    
reference_commands = """
cd python-webob-1.1.1/ ; dch local build ; dpkg-buildpackage -S -sa ; cd ..
cowpoke underscore_1.1.6-1~bpo60+1.1.dsc 
rsync -av root@builder:/var/cache/pbuilder/amd64/squeeze/result/ result/
dput cypress result/ruby-json_1.6.1-1~bpo60+1.1_amd64.changes 
cowpoke --arch=i386 --create --dpkg-opts='-B' ruby-json_1.6.1-1~bpo60+1.1.dsc   rsync -av root@builder:/var/cache/pbuilder/i386/squeeze/result/ result.i386/
dput cypress result.i386/ruby-json_1.6.1-1~bpo60+1.1_i386.changes 
"""    
