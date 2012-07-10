import os
import subprocess

from debrepos.repos import RepRepRo
from debrepos.build import MainBuilder
from debrepos.base import parse_dsc_filename
from debrepos.base import get_filenames_with_dcmd
from debrepos.config import config

DEBIAN_BASEDIR = config.get('repos_debian', 'basedir')
LOCAL_BASEDIR = config.get('repos_local', 'basedir')



class MainManager(object):
    def __init__(self):
        self.builder = MainBuilder(user='root')
        self.debian_repos = RepRepRo(basedir=DEBIAN_BASEDIR)
        self.local_repos = RepRepRo(basedir=LOCAL_BASEDIR)
        self.srcbuild_opts = ['-S', '-sa', '-us', '-uc']

    def staging_dir(self, dscfile):
        source, version = parse_dsc_filename(dscfile)
        return source

    def get_dscfile_from_changes(self, changes):
        dscfile = ''
        filenames = get_filenames_with_dcmd(changes)
        for filename in filenames:
            if filename.endswith('.dsc'):
                if not dscfile:
                    dscfile = os.path.basename(filename)
                else:
                    print "Already a dscfile", dscfile
                    print "filename", filename
                    raise RuntimeError, "too many .dsc's"
        if not dscfile:
            raise RuntimeError, "No .dsc found."
        return dscfile
    
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
        
    def install_to_repos(self, dist, changes):
        dscfile = self.get_dscfile_from_changes(changes)
        source, version = parse_dsc_filename(dscfile)
        if os.path.isfile(changes):
            self.local_repos.include(dist, changes)
        self.build_binary_packages(dscfile)
        here = os.getcwd()
        os.chdir(source)
        changes_files = [f for f in os.listdir('.') if f.endswith('.changes')]
        for changes in changes_files:
            self.local_repos.include(dist, changes)
            
if __name__ == '__main__':
    m = MainManager()
    kel = 'kde-extra-looks_0.3.2.dsc'
    f = 'frotz_2.43-3.dsc'

    
    
    
    
