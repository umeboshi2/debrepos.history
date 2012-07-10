import os, sys
from ConfigParser import ConfigParser
from StringIO import StringIO

default_config = """
# configuration file for debrepos
# all options starting with "__" are not used in the code,
# but are here to ease editing this file

[DEFAULT]
homedir:    /freespace/debrepos
server_default_port:    8000

[main]


[server]
address:    0.0.0.0
port:    %(server_default_port)s
#pidfile:    /var/run/debrepos.pid
pidfile:    /tmp/debrepos.pid

[somesection]
option:    value

[repos_debian]
basedir:    %(homedir)s/debian

[repos_security]
basedir:    %(homedir)s/security

[repos_local]
basedir:    %(homedir)s/paella

[client]
server:    cypress
port:    %(server_default_port)s


""" 

config_path = '/etc/debrepos.cf'

class DebReposConfig(ConfigParser):
    def __init__(self):
        ConfigParser.__init__(self)
        
    def get_xy(self, section, option):
        strvalue = self.get(section, option)
        x, y = [int(v.strip()) for v in strvalue.split(',')]
        return x, y

    def get_list(self, section, option, sep=','):
        value = self.get(section, option)
        return [v.strip() for v in value.split(sep)]
    
    def reload_config(self):
        self.read([self.configfilename])
        

def get_config():
    if os.path.isfile(config_path):
       contents = file(config_path).read()
    else:
        contents = default_config
    cfile = StringIO()
    cfile.write(contents)
    cfile.seek(0)
    cfg = DebReposConfig()
    cfg.readfp(cfile)
    return cfg


# make a global object
config = get_config()

if __name__ == '__main__':
    print 'testing config module'
    
