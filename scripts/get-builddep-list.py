#!/usr/bin/env python
import os, sys
import subprocess
from StringIO import StringIO

BUILDHOST = 'builder'
BUILDUSER = 'root'

BUILDDEP_SCRIPT = """#!/bin/bash
xargs apt-get -y build-dep -s | grep ^Inst | gawk '{print $2 "\tinstall"}'
"""

def poll_process_for_complete_output(cmd):
    output = StringIO()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        nextline = proc.stdout.readline()
        if nextline == '' and proc.poll() is not None:
            break
        output.write(nextline)
        output.flush()
    if proc.returncode:
        msg = "There was a problem with command: %s" % cmd
        raise RuntimeError, msg
    output.seek(0)
    return output



def send_script():
    filename = '/tmp/prepare-builddeps'
    scriptfile = file(filename, 'w')
    scriptfile.write(BUILDDEP_SCRIPT)
    scriptfile.close()
    subprocess.check_call(['chmod', '+x', filename])
    scp = ['scp', filename, 'root@builder:/usr/local/bin']
    subprocess.check_call(scp)


def get_builddeps(package):
    print "Getting build dependencies for %s" % package
    address = '%s@%s' % (BUILDUSER, BUILDHOST)
    cmd = ['ssh', address, 'prepare-builddeps']
    package_data = '%s\n' % package
    lines = []
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    proc.stdin.write(package_data)
    proc.stdin.close()
    proc.wait()
    err = proc.stderr.read()
    if err:
        print "ERROR:", err
        return lines
    
    for line in proc.stdout:
        lines.append(line.strip())
    return lines


def make_builddeps_list(packages):
    package_set = set()
    for package in packages:
        for line in get_builddeps(package):
            package_set.add(line)
        print "We have %d packages in the set." % len(package_set)
    return package_set


def get_packages_from_selections(selections=None):
    packages = []
    if selections is None:
        cmd = ['dpkg', '--get-selections']
        output = poll_process_for_complete_output(cmd)
    else:
        output = StringIO(selections)
        
    for line in output:
        package, action = [x.strip() for x in line.split()]
        packages.append(package)
    return packages


def get_builddeps_from_selections(selections=None):
    packages = get_packages_from_selections(selections=selections)
    package_set = make_builddeps_list(packages)
    return package_set

def make_package_list(package_set, filename='builddeps'):
    package_list = list(package_set)
    package_list.sort()
    print "Writing %d packages to file %s" % (len(package_list), filename)
    out = file(filename, 'w')
    for package in package_list:
        out.write('%s\n' % package)
    out.close()
    return filename


if __name__ == '__main__':
    ss = send_script
    gb = get_builddeps
    p = 'xemacs'
    ss()
    gb(p)
    gpfs = get_packages_from_selections
    gbfs = get_builddeps_from_selections
    sel = file('/freespace/debrepos/debian/conf/pkgs/squeeze.pkgs').read()
    packages = gbfs(selections=sel)
    make_package_list(packages)
    
    
    

