from string import Template


MAINTEMPLATE = """MIRRORSITE=$mirrorsite
DISTRIBUTION=$dist
DEBOOTSTRAP=$debootstrap
DEBOOTSTRAPOPTS=('--variant=buildd' '--keyring=/etc/apt/trusted.gpg')
APTCACHE=""
DEBBUILDOPTS=$debbuild_opts
PBUILDERSATISFYDEPENDSCMD=/usr/lib/pbuilder/pbuilder-satisfydepends
OTHERMIRROR="$othermirrors"
EXTRAPACKAGES=""
HOOKDIR=/etc/pbuilder/hooks
# exported variables go below this line
export CFLAGS="$cflags"
export DEB_BUILD_OPTIONS="$deb_build_options"
"""

    
    
class PbuilderConfigManager(object):
    def __init__(self):
        self.template = Template(MAINTEMPLATE)
        self.mirrorsite = 'http://cypress.forest/debrepos/debian'
        self.dist = 'squeeze'
        self.debootstrap = 'cdebootstrap'
        self.debbuild_opts = ''
        self.other_mirrors = []
        self.cflags = '-pipe'
        self.deb_build_options = 'parallel=3'


    def make_mirrorsite_entries(self, host, dist):
        self.other_mirrors = []
        self.mirrorsite = 'http://%s/debrepos/debian' % host
        baseurl = 'http://%s/debrepos/paella' % host
        dists = [dist, '%s-backports' % dist]
        components = 'main contrib non-free'
        for d in dists:
            omirror = 'deb %s %s %s' % (baseurl, d, components)
            self.other_mirrors.append(omirror)
            
    def make_data(self):
        keys = ['mirrorsite', 'dist', 'debootstrap',
                'debbuild_opts', 'cflags', 'deb_build_options']
        data = dict()
        for key in keys:
            data[key] = getattr(self, key)
        data['othermirrors'] = '|'.join(self.other_mirrors)
        return data

    def substitute(self):
        data = self.make_data()
        return self.template.substitute(data)
    
    
        
        



    
        
if __name__ == '__main__':
    bp = BullProdder()


    
    
    
    
        
if __name__ == '__main__':
    bp = BullProdder()


    
    
    
    
