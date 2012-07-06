from ConfigParser import ConfigParser

DIST_LABEL_ATTS = [
    'origin',
    'label',
    'suite',
    'version',
    'codename',
    'architectures',
    'components',
    'description',
    'log',
    'update',
    'signwith'
    ]

DIST_LABELS = dict()
for att in DIST_LABEL_ATTS:
    DIST_LABELS[att] = att.capitalize()
DIST_LABELS['signwith'] = 'SignWith'


class Distribution(object):
    origin = 'Debian'
    label = 'Debian'
    suite = 'stable'
    version = '6.0'
    codename = 'squeeze'
    architectures = []
    components = ['main', 'contrib', 'non-free']
    description = 'Debian Stable'
    log = 'logfile'
    update = ''
    signwith = ''

    def __str__(self):
        content = ''
        for att in DIST_LABEL_ATTS:
            label = DIST_LABELS[att]
            value = getattr(self, att)
            if value:
                if type(value) is list:
                    value = ' '.join(value)
                content += '%s: %s\n' % (label, value)
        return content
    
class Update(object):
    name = 'main'
    method = 'http://ftp.us.debian.org/debian'
    fallback = 'http://ftp.de.debian.org/debian'
    verify = '473041FA'
    architectures = []
    components = ['main', 'contrib', 'non-free']
    udeb_components = 'none'
    filterlist = []
    
    
class ReposConfig(ConfigParser):
    pass


if __name__ == '__main__':
    d = Distribution()
    
