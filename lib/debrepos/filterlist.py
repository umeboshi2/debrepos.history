

def make_pkg_line(package, action):
    # These are magic numbers to more closely mimic
    # the output of dpkg --get-selections
    truetab = 6 - (len(package) / 8)
    tabs = '\t' * truetab
    if not tabs:
        tabs = '\t'
    line = '%s%s%s\n' % (package, tabs, action)
    return line


def selections_to_dictionary(fileobj, install=False):
    data = dict()
    for line in fileobj:
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
            if install:
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
    return file_to_dictionary(file(filename))

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
        data = file_to_dictionary(file(filename))
        master_data.update(data)
    print "Updating %s with all gathered data" % master_filename
    make_master_file(dist, master_data)
    
