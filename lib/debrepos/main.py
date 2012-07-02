import os
import subprocess

from debrepos.repos import RepRepRo
from debrepos.build import MainBuilder
from debrepos.base import parse_dsc_filename

DEBIAN_BASEDIR = '/freespace/debrepos/debian'
PAELLA_BASEDIR = '/freespace/debrepos/paella'


class MainManager(object):
    def __init__(self):
        self.builder = MainBuilder(user='root')
        self.debian_repos = RepRepRo(basedir=DEBIAN_BASEDIR)
        self.paella_repos = RepRepRo(basedir=PAELLA_BASEDIR)
        self.srcbuild_opts = ['-S', '-sa', '-us', '-uc']

    def staging_dir(self, dscfile):
        source, version = parse_dsc_filename(dscfile)
        return source
    
    def build_source_package(self, dscfile):
        source, version = parse_dsc_filename(dscfile)
        upstream_version = version.split('-')[0]
        dirname = '%s-%s' % (source, upstream_version)
        here = os.getcwd()
        os.chdir(dirname)
        cmd = ['dpkg-buildpackage'] + self.srcbuild_opts
        subprocess.check_call(cmd)
        os.chdir(here)
        #self.builder.stage_resulting_changes(dscfile, 'source')
        changes = '%s_%s_source.changes' % (source, version)
        self.builder.stage_changes(source, changes, 'source', remove=False)
        return source
    
    def build_binary_packages(self, dscfile):
        self.builder.build(dscfile)


    def build(self, dscfile):
        source = self.build_source_package(dscfile)
        basename = os.path.basename(dscfile)
        here = os.getcwd()
        os.chdir(source)
        self.build_binary_packages(basename)
        os.chdir(here)
        
    def install_to_repos(self, dist, dscfile):
        source, version = parse_dsc_filename(dscfile)
        changes = '%s_%s_source.changes' % (source, version)
        if os.path.isfile(changes):
            self.paella_repos.include(dist, changes)
        self.build_binary_packages(dscfile)
        here = os.getcwd()
        os.chdir(source)
        changes_files = [f for f in os.listdir('.') if f.endswith('.changes')]
        for changes in changes_files:
            self.paella_repos.include(dist, changes)
            
if __name__ == '__main__':
    m = MainManager()
    kel = 'kde-extra-looks_0.3.2.dsc'
    f = 'frotz_2.43-3.dsc'

    
    
    
    
