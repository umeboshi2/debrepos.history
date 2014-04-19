import os
import subprocess
import tempfile

from debrepos.path import path

from debrepos.util import hardlink_dupes, chmod

PRODUCT_TYPES = ['pro', 'home']
LICENSE_TYPES = ['retail', 'oem', 'vlk']

LTYPE = dict(vlk='vol', oem='oem', retail='fpp')
PTYPE = dict(pro='p', home='h')

XP_ISO_DIR = '/freespace/shared/common/disk_images/iso/winxp-iso'
ALLWIN_ISO = '/freespace/shared/common/disk_images/iso/allwin/allwin-dvd-1.iso'

def xp_basename(product, license):
    lic = LTYPE[license]
    prod = PTYPE[product]
    return 'wx%s%s' % (prod, lic)


def iso_basename(product, license, language='en'):
    xpbase = xp_basename(product, license)
    return '%s_%s.iso' % (xpbase, language)


def mount_iso(product, license, target=None):
    iso = os.path.join(XP_ISO_DIR, iso_basename(product, license))
    if target is None:
        target = xp_basename(product, license)
    if not os.path.isdir(target):
        os.makedirs(target)
    cmd = ['fuseiso', iso, target]
    subprocess.check_call(cmd)

def umount_iso_pl(product, license):
    xpbase = xp_basename(product, license)
    cmd = ['fusermount', '-u', xpbase]
    subprocess.check_call(cmd)
    

def umount_iso(mountpoint):
    cmd = ['fusermount', '-u', mountpoint]
    subprocess.check_call(cmd)
    

def copy_winxp_contents(winxpdir, target):
    if not os.path.isdir(target):
        os.makedirs(target)
    archdir = os.path.join(winxpdir, 'i386')
    cmd = ['cp', '-a', archdir, target]
    print "Copying windows xp contents with command: %s" % ' '.join(cmd)
    subprocess.check_call(cmd)

def extract_files_from_iso(product, license, target):
    if not os.path.isdir(target):
        os.makedirs(target)
    xpbasename = xp_basename(product, license)
    dest = os.path.join(target, xpbasename)
    mountpoint = tempfile.mkdtemp('', 'winxpiso-mount-')
    mount_iso(product, license, target=mountpoint)
    copy_winxp_contents(mountpoint, dest)
    umount_iso(mountpoint)
    os.rmdir(mountpoint)
    print "Files extracted for Windows XP %s %s" % (product, license)
    

def fix_oem_directory(directory):
    directory = path(directory)
    archdir = directory / 'i386'
    oemdir = directory / 'OEM'
    if oemdir.isdir():
        uglypath = archdir / '$oem$/$1'
        uglypath.makedirs()
        oem_lower = uglypath / 'oem'
        if oem_lower.isdir():
            raise RuntimeError, "%s shouldn't exist." % oem_lower
        oemdir.rename(oem_lower)
    #cmd = ['perl', opts.lc_script, directory]
    #subprocess.check_call(cmd)
    for filename in directory.walk():
        dirname, basename = filename.splitpath()
        lower = basename.lower()
        if basename != lower:
            newname = dirname / lower
            if newname.exists():
                raise RuntimeError , "%s already exists" % newname
            print "Renaming %s to %s in %s" % (basename, lower, dirname)
            os.rename(filename, newname)
            

def hardlink_winxp_dupes(directories):
    for directory in directories:
        chmod(directory, '+w')
    hardlink_dupes(directories)
    for directory in directories:
        fix_oem_directory(directory)
    for directory in directories:
        chmod(directory, 'a-w')
    for directory in directories:
        chmod(directory, '755', recursive=False)
    

if __name__ == '__main__':
    for p in PRODUCT_TYPES:
        for l in LICENSE_TYPES:
            #print iso_basename(p, l)
            #mount_iso(p, l)
            extract_files_from_iso(p, l, 'os.tst')
    os.chdir('os.tst')
    dirs = os.listdir('.')
    hardlink_winxp_dupes(dirs)
    
