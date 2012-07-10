import os, sys
import glob
from distutils.core import setup


from distutils.command.clean import clean as _clean
from distutils.command.build import build as _build

def get_version(astuple=False):
    topline = file('debian/changelog').next()
    VERSION = topline[topline.find('(')+1 :topline.find(')')].split('.')
    print 'VERSION is', VERSION
    if len(VERSION) > 2:
        for character in '-+':
            if character in VERSION[2]:
                VERSION = VERSION[0:2] + [VERSION[2].split(character)[0]]
    if astuple:
        return tuple(VERSION)
    else:
        return '.'.join(map(str, VERSION))

class clean(_clean):
    def run(self):
        _clean.run(self)
        here = os.getcwd()
        for root, dirs, files in os.walk(here):
            for afile in files:
                if afile.endswith('~'):
                    os.remove(os.path.join(root, afile))
                if afile.endswith('.pyc'):
                    os.remove(os.path.join(root, afile))
        print "removing docs/html (if there)"
        os.system('rm -fr docs/html')


data_files = []

PACKAGES = ['common', 'server', 'client']
package = None

if sys.argv[1] in PACKAGES:
    package = sys.argv[1]
    del sys.argv[1]
else:
    print "No packages found"
    sys.exit(0)
    

if package is None:
    print "args", sys.argv
    #print os.environ
    for k,v in os.environ.items():
        print '%s: %s' % (k,v)
    raise RuntimeError, "bad news"

pd = {'' : 'lib'}

PACKS = {
    'common' : ['debrepos']
    }


if package == 'common':
    packages = ['debrepos']
else:
    packages = []
    
_myfindcmdforpackages = 'find src -type d | grep -v svn | cut -f2- -d/'
url = 'http://paella.berlios.de'
version = get_version()
author_email = 'umeboshi3@gmail.com'
author = 'Joseph Rawson'
description = 'paella configuration/installation management system',



setup(name='debrepos-'+package,
      version=version,
      description=description,
      author=author,
      author_email=author_email,
      url=url,
      data_files=data_files,
      cmdclass=dict(clean=clean),
      package_dir={'':'lib'},
      packages=packages
      )
