import subprocess

class Proc(subprocess.Popen):
    def __init__(self, cmd, **kw):
        subprocess.Popen.__init__(self, cmd, **kw)
        self.command_line = cmd
        

class SecureShellHandler(object):
    def __init__(self, host, user=None):
        self.host = host
        self.user = user
        
    def _check_subprocess(self, command, returncode):
        if isinstance(command, Proc):
            command = command.command_line
        if returncode:
            cmd = ' '.join(command)
            raise subprocess.CalledProcessError(returncode, cmd)

    def _address(self):
        address = self.host
        if self.user is not None:
            address = '%s@%s' % (self.user, self.host)
        return address
            
    def command_prefix(self, user=None):
        orig = None
        if user is not None:
            orig = self.user
            self.user = user
        address = self._address()
        if orig:
            self.user = orig
        return ['ssh', address]

    # This method is for small files only.
    def get_file_contents(self, filename):
        cmd = self.command_prefix()
        cmd += ['cat', filename]
        proc = Proc(cmd, stdout=subprocess.PIPE)
        contents = proc.stdout.read()
        retval = proc.wait()
        self._check_subprocess(cmd, retval)
        return contents

    # This method is for small files only.
    def send_file_contents(self, filename, contents, user=None):
        cmd = self.command_prefix(user=user)
        cmd += ['dd', 'of=%s' % filename]
        proc = Proc(cmd, stdin=subprocess.PIPE, stderr=file('/dev/null', 'w'))
        proc.stdin.write(contents)
        proc.stdin.close()
        retval = proc.wait()
        self._check_subprocess(cmd, retval)

    def copy_remote_file(self, src, dest, options=[], user=None):
        cmd = self.command_prefix(user=user)
        cmd.append('cp')
        cmd += options
        cmd += [src, dest]
        subprocess.check_call(cmd)

    def rename_remote_file(self, src, dest, options=[], user=None):
        cmd = self.command_prefix(user=user)
        cmd.append('mv')
        cmd += options
        cmd += [src, dest]
        subprocess.check_call(cmd)

    # just simple tests for files and directories
    def _test(self, testopt, value, user=None):
        cmd = self.command_prefix(user=user)
        cmd += ['test', testopt, value]
        retval = subprocess.call(cmd)
        if retval:
            return False
        else:
            return True
        
    def isdir(self, filename, user=None):
        return self._test('-d', filename, user=user)
    
    def isfile(self, filename, user=None):
        return self._test('-f', filename, user=user)

    def exists(self, filename, user=None):
        return self._test('-e', filename, user=user)

    def makedirs(self, fullpath, user=None):
        cmd = self.command_prefix(user=user)
        cmd += ['mkdir', '-p', fullpath]
        subprocess.check_call(cmd)
        
        
def parse_dsc_filename(dscfile):
    if '_' not in dscfile:
        raise RuntimeError , "No underscore in %s" % dscfile
    if not dscfile.endswith('.dsc'):
        raise RuntimeError , "%s doesn't end in .dsc" % dscfile
    source, remainder = dscfile.split('_')
    version = remainder.split('.dsc')[0]
    return source, version    


# filename should be either *.dsc or *.changes
def get_filenames_with_dcmd(filename):
    cmd = ['dcmd', filename]
    proc = Proc(cmd, stdout=subprocess.PIPE)
    retval = proc.wait()
    filenames = [line.strip() for line in proc.stdout]
    return filenames
