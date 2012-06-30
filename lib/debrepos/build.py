import os
import time
import signal
import subprocess

from useless.base.path import path

from debrepos.base import Proc, SecureShellHandler


class BullProdder(SecureShellHandler):
    def __init__(self, dist='squeeze', arch='i386',
                 buildd='builder', user=None):
        SecureShellHandler.__init__(self, buildd, user=user)
        self.arch = arch
        self.dist = dist
        # this should also be self.host
        self.buildd = buildd
        # this should also be self.user
        self.buildd_user = user
        
        self.buildd_incoming = 'cowbuilder-incoming'

        
        self.verbose = False
        self.watch_build_process = False
        self.tailproc = None
        self.buildproc = None
        self.build_logfile = None
        self.logdir = path.getcwd() / 'logs'
        if not self.logdir.isdir():
            self.logdir.makedirs()
            
        self.system_pbuilderrc_filename = '%s-pbuilderrc' % self.host
        self.dpkg_opts = []
        self.current_package = None

        self.local_pbuilderrc_config_dir = 'pbuilderrc'
        

    def _check_subprocess_test(self, *args):
        SecureShellHandler._check_subprocess(self, *args)
        if self.tailproc is not None:
            self.terminate_tailproc()

    def make_tailproc(self, logname):
        if self.verbose:
            print "Creating tail process...."
        cmd = ['x-terminal-emulator', '-T', logname]
        cmd += ['-e', 'tail', '-f', logname]
        self.tailproc = Proc(cmd)

    def terminate_tailproc(self):
        if self.verbose:
            print "Terminating tail process...."
        pid = self.tailproc.pid
        os.kill(pid, signal.SIGTERM)
        self.tailproc = None

    def resultdir(self):
        return 'result/%s' % self.arch

    def basedir(self, pbuilderrc=None):
        basedir = '/var/cache/pbuilder/%s/%s/base.cow'
        basedir = basedir % (self.arch, self.dist)
        if pbuilderrc is not None:
            basedir = '%s.%s' % (basedir, pbuilderrc)
        return basedir

    def incomingdir(self):
        user = self.buildd_user
        if user is None:
            user = ''
        incoming = '~%s/%s' % (user, self.buildd_incoming)
        return incoming

    def pbuilderrc(self, pbuilderrc):
        incoming = self.incomingdir()
        return os.path.join(incoming, 'pbuilderrc-%s' % pbuilderrc)

    def buildresult(self, pbuilderrc=None):
        base = os.path.join('/var/cache/pbuilder',
                             self.arch, self.dist)
        rpath = os.path.join(base, 'result')
        if pbuilderrc is not None:
            rpath = os.path.join(base, pbuilderrc, 'result')
        return rpath

    def logname(self, command):
        templ = '%s_%s-%s-%s.log'
        logname = templ % (command, self.host, self.arch, self.dist)
        return self.logdir / logname

    def _cowbuild_cmd(self, command, cowbase, pbuilderrc, user):
        prefix = self.command_prefix(user=user)
        cmd = prefix + ['cowbuilder', command, '--basepath', cowbase]
        cmd += self._update_cowbuild_cmd(pbuilderrc)
        return cmd

    def _update_cowbuild_cmd(self, pbuilderrc):
        cmd = []
        if pbuilderrc is not None:
            cmd += ['--configfile', self.pbuilderrc(pbuilderrc)]
        return cmd
    
    def update_base(self, pbuilderrc=None):
        cowbase = self.basedir(pbuilderrc=pbuilderrc)
        cmd = self._cowbuild_cmd('--update', cowbase, pbuilderrc, 'root')
        logname = self.logname('update')
        logfile = file(logname, 'a+')
        subprocess.check_call(cmd, stdout=logfile, stderr=logfile)
        logfile.close()

    def create_base(self, pbuilderrc=None):
        cowbase = self.basedir(pbuilderrc=pbuilderrc)
        
        prefix = self.command_prefix(user='root')
        distdir, basename = os.path.split(cowbase)
        if not self.isdir(cowbase, user='root'):
            if self.verbose:
                print '%s not found in %s' % (basename, distdir)
            # create parent directory
            self.makedirs(distdir, user='root')

            # doublecheck existence of directory
            if self.verbose:
                print "Make sure %s exists on %s." % (distdir, self.host)
            if not self.isdir(distdir, user='root'):
                msg = "%s doesn't exist on %s."
                msg = msg % (distdir, self.host)
                raise RuntimeError , msg
            cmd = prefix + ['cowbuilder', '--create',
                            '--dist', self.dist,
                            '--basepath', cowbase]
            cmd += self._update_cowbuild_cmd(pbuilderrc)
            logname = self.logname('create')
            logfile = file(logname, 'w')
            subprocess.check_call(cmd, stdout=logfile, stderr=logfile)
            # /CurrentlyBuilding is used to keep man-db from spending
            # time building an unused man database.
            currently_building = os.path.join(cowbase, 'CurrentlyBuilding')
            cmd = prefix + ['touch', currently_building]
            subprocess.check_call(cmd)
        else:
            if self.verbose:
                print cowbase, 'already exists.'

    def retrieve_result(self, pbuilderrc=None):
        address = self.command_prefix(user='root')[1]
        rpath = self.buildresult(pbuilderrc=pbuilderrc)
        src = '%s:%s/' % (address, rpath)
        dest = '%s/' % self.resultdir()
        if not os.path.isdir(dest):
            os.makedirs(dest)
        options = '-a'
        if self.verbose:
            options = '-av'
        cmd = ['rsync', options, src, dest]
        if self.verbose:
            print "Retrieving result with: %s" % ' '.join(cmd)
        subprocess.check_call(cmd)

    def make_prebuild_info(self, logfile, pbuilderrc):
        divider = '=' * 70 + '\n'
        if pbuilderrc is not None:
            logfile.write('Using pbuilderrc: %s\n' % pbuilderrc)
            logfile.write(divider)
            contents = self.get_pbuilderrc_contents(pbuilderrc)
            logfile.write(contents)
            logfile.write(divider)
        else:
            logfile.write('Using system pbuilderrc\n')
            logfile.write(divider)

    def build(self, dscfile, pbuilderrc=None, wait=True):
        incoming = '~/%s' % self.buildd_incoming
        self.makedirs(incoming)
        
        # copy files to buildd
        if self.verbose:
            print "Copying files to %s" % self.host
        cmd = ['dcmd', 'scp', dscfile,
               '%s:~/%s' % (self.host, self.buildd_incoming)]
        subprocess.check_call(cmd)

        # prepare variables and logs
        basepath = self.basedir(pbuilderrc=pbuilderrc)
        buildresult = self.buildresult(pbuilderrc=pbuilderrc)
        package = os.path.basename(dscfile).split('.dsc')[0]
        self.current_package = package
        logname = self.logname('build.%s' % package)
        self.build_logfile = logname
        logfile = file(logname, 'a')
        self.make_prebuild_info(logfile, pbuilderrc)

        # prepare build command
        prefix = self.command_prefix(user='root')
        buildcmd = ['cowbuilder', '--build', '--basepath', basepath,
                    '--buildresult', buildresult]
        buildcmd += self._update_cowbuild_cmd(pbuilderrc)
        buildcmd.append(dscfile)

        # setup command for remote execution
        shell_cmd = ' '.join(buildcmd)
        dirspec = self.incomingdir()
        ssh_cmd = 'cd %s && %s' % (dirspec, shell_cmd)

        cmd = prefix + [ssh_cmd]
        if self.verbose:
            msg = "building source %s with command: %s" 
            print msg % (package, ' '.join(cmd))

        # run command
        self.buildproc = Proc(cmd, stdout=logfile, stderr=logfile)

        if self.watch_build_process:
            self.make_tailproc(logname)
        if wait:
            while self.poll() is None:
                time.sleep(10)
            self.build_finished()


    def poll(self):
        retval = self.buildproc.poll()
        if retval is not None:
            if self.tailproc is not None:
                print "Terminating tailproc", self.tailproc
                self.terminate_tailproc()
            if self.verbose and not retval:
                package = self.current_package
                print "build of source %s completed successfully." % package
        return retval

    def build_finished(self):
        self.current_package = None
        self.buildproc = None
        self.current_pbuilderrc = None
        self.current_dscfile = None

    def remove_uploaded_sources(self, filenames):
        if self.verbose:
            print "removing uploaded sources from %s" % self.host
        incoming = self.buildd_incoming
        filenames = [os.path.join(incoming, f) for f in filenames]
        cmd = self.command_prefix()
        cmd += ['rm'] + filenames
        subprocess.check_call(cmd)

    def get_system_pbuilderrc(self):
        return self.get_file_contents('/etc/pbuilderrc', user='root')

    def send_system_pbuilderrc(self, contents):
        self.send_file_contents('/etc/pbuilderrc', contents, user='root')

    def backup_system_pbuilderrc(self):
        filename = self.system_pbuilderrc_filename
        if os.path.isfile(filename):
            print "pbuilderrc on %s already looks backed up" % self.host
            return
        pbuilderrc = file(filename, 'w')
        contents = self.get_system_pbuilderrc()
        pbuilderrc.write(contents)
        pbuilderrc.close()

    def restore_system_pbuilderrc(self):
        filename = self.system_pbuilderrc_filename
        if not os.path.isfile(filename):
            raise RuntimeError , "%s not available" % filename
        contents = file(filename).read()
        self.send_system_pbuilderrc(contents)

    def get_pbuilderrc_contents(self, pbuilderrc):
        filename = os.path.join(self.local_pbuilderrc_config_dir, pbuilderrc)
        return file(filename).read()

    def send_pbuilderrc(self, pbuilderrc):
        contents = self.get_pbuilderrc_contents(pbuilderrc)
        remote_filename = self.pbuilderrc(pbuilderrc)
        self.send_file_contents(remote_filename, contents)

    
    
        
if __name__ == '__main__':
    bp = BullProdder()


    
    
    
    
