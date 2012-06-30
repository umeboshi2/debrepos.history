import os, sys
import subprocess

from useless.base.path import path

class ProcessRunning(Exception):
    pass


class RepRepRo(object):
    def __init__(self, basedir=None):
        if basedir is None:
            basedir = path.getcwd()
        self.basedir = path(basedir)
        self.logfile_name = self.basedir / 'logs/debrepos.log'
        self.logfile = None
        self.clean_proc()
        self.open_logfile()
        
    def check_proc(self):
        if self.proc is not None:
            return self.proc.poll()
        else:
            return 'empty'
        
    def clean_proc(self):
        self.proc = None
        self.running = ''
        
    def open_logfile(self):
        self.logfile = file(self.logfile_name, 'a')

    def close_logfile(self):
        self.logfile.close()
        
    def _set_options(self):
        options = ['--basedir', self.basedir]
        options += ['-VV', '--noskipold']
        return options
    
    def update(self, codenames=[]):
        cmd = ['reprepro', '-VV', '--noskipold', 'update']
        cmd = ['reprepro'] + self._set_options()
        cmd += ['update']
        cmd += codenames
        if self.proc is None:
            self.proc = subprocess.Popen(cmd, stdout=self.logfile,
                                         stderr=self.logfile)
        else:
            raise ProcessRunning , "There is already a process running"




if __name__ == '__main__':
    r = RepRepRo(basedir='/freespace/debrepos/debian')
    
    
    
    
