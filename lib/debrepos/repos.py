import os, sys
import subprocess

from debrepos.path import path

class ProcessRunning(Exception):
    pass


class RepRepRo(object):
    def __init__(self, basedir=None):
        if basedir is None:
            basedir = path.getcwd()
        self.set_basedir(basedir)
        self.clean_proc()


    def set_basedir(self, basedir):
        self.basedir = path(basedir)
        self.logfile_name = self.basedir / 'logs/debrepos.log'
        self.logfile = None
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

    def run_command(self, command, logfile=None):
        if logfile is None:
            logfile = self.logfile
        if self.proc is None:
            self.proc = subprocess.Popen(command, stdout=logfile,
                                         stderr=logfile)
        else:
            raise ProcessRunning , "There is already a process running"
        
    def update(self, codenames=[]):
        cmd = ['reprepro'] + self._set_options()
        cmd += ['update']
        cmd += codenames
        self.run_command(cmd)

    def include(self, codename, changes):
        cmd = ['reprepro'] + self._set_options()
        cmd += ['--ignore=wrongdistribution']
        cmd += ['include', codename, changes]
        self.run_command(cmd)
        retcode = self.proc.wait()
        if retcode:
            raise RuntimeError , "bad things happening"
        self.clean_proc()
        


if __name__ == '__main__':
    r = RepRepRo(basedir='/freespace/debrepos/debian')
    
    
    
    
