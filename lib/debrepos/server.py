import SimpleXMLRPCServer

from useless.base.path import path

from debrepos.filterlist import selections_to_dictionary
from debrepos.filterlist import make_pkg_line
from debrepos.repos import RepRepRo

class PartialMirrorManager(object):
    def __init__(self):
        self.baseparent = path('/freespace/debrepos')
        self.repos = RepRepRo()
        
    def _main_list_filename(self, dist):
        basename = '%s.pkgs' % dist
        directory = self.baseparent / 'debian/conf/pkgs'
        filename = directory / basename
        return filename

    def main_list_filename(self, dist):
        return str(self._main_list_filename(dist))
    

    def get_selections(self, dist):
        filename = self._main_list_filename(dist)
        if not filename.isfile():
            return {}
        else:
            return selections_to_dictionary(filename, install=True)
        

    def update_list(self, dist, data):
        master = self.get_selections(dist)
        filename = self._main_list_filename(dist)
        master.update(data)
        if not filename.isfile():
            print "Creating new file: %s" % filename
        mainlist = file(filename, 'w')
        packages = master.keys()
        packages.sort()
        for package in packages:
            action = master[package]
            line = make_pkg_line(package, action)
            mainlist.write(line)
        mainlist.close()
        return True
    
    def update_repos(self, repos):
        if repos == 'debian':
            basedir = self.baseparent / 'debian'
        elif repos == 'security':
            basedir = self.baseparent / 'security'
        else:
            msg = "%s not a valid repository" % repos
            raise RuntimeError , msg
        self.repos.set_basedir(basedir)
        ready = False
        check = self.repos.check_proc()
        if check and check == 'empty':
            ready = True
        elif check == 0:
            self.repos.clean_proc()
            ready = True
        if not ready:
            raise RuntimeError , "repos process not ready"
        self.repos.update()
        return True
    
def make_server(host, port, instance):
    server = SimpleXMLRPCServer.SimpleXMLRPCServer((host, port))
    server.register_instance(instance)
    return server



if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'client':
        import xmlrpclib
        remote = xmlrpclib.Server('http://cypress:8000')
        r = remote
    else:
        srv = PartialMirrorManager()
        server = make_server('0.0.0.0', 8000, srv)
        server.serve_forever()
        

    
