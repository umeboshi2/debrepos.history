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
    def get_file_contents(self, filename, user=None):
        cmd = self.command_prefix(user=user)
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


### code to help handle package selection files..
##################################################

def make_pkg_line(package, action):
    # These are magic numbers to more closely mimic
    # the output of dpkg --get-selections
    truetab = 6 - (len(package) / 8)
    tabs = '\t' * truetab
    if not tabs:
        tabs = '\t'
    line = '%s%s%s\n' % (package, tabs, action)
    return line


def selections_to_dictionary(filename):
    data = dict()
    for line in file(filename):
        line = line.strip()
        package, action = [i.strip() for i in line.split()]
        #print '%s: %s' % (package, action)
        multiarch_stripped = False
        if ':' in package:
            print "multiarch detected: %s" % package
            package = package.split(':')[0]
            multiarch_stripped = True
        if package in data and not multiarch_stripped:
            msg = 'Package %s already present...' % package
            raise RuntimeError, msg
        else:
            if opts.install:
                action = 'install'
            if action != 'install':
                print "WARNING: %s set for action %s" % (package, action)
            data[package] = action
    return data

file_to_dictionary = selections_to_dictionary

MASTERLISTS = dict(squeeze='squeeze.pkgs',
                   wheezy='wheezy.pkgs',
                   sid='sid.pkgs'
                   )


def get_master_list(dist):
    filename = MASTERLISTS[dist]
    return file_to_dictionary(filename)

def make_master_file(dist, data):
    master_filename = MASTERLISTS[dist]
    mfile = file(master_filename, 'w')
    packages = data.keys()
    packages.sort()
    for package in packages:
        action = data[package]
        line = make_pkg_line(package, action)
        mfile.write(line)
    mfile.close()
        
    
def update_master_list(dist, filenames):
    master_filename = MASTERLISTS[dist]
    if not os.path.isfile(master_filename):
        print "creating new file: %s" % master_filename
        m = file(master_filename, 'w')
        m.close()
    master_data = get_master_list(opts.dist)
    for filename in filenames:
        print "updating %s with %s" % (master_filename, filename)
        data = file_to_dictionary(filename)
        master_data.update(data)
    print "Updating %s with all gathered data" % master_filename
    make_master_file(dist, master_data)
    
