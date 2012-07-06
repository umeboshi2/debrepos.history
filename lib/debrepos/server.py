import SimpleXMLRPCServer

from useless.base.path import path

from debrepos.filterlist import selections_to_dictionary


class TestService(object):
    def __init__(self):
        self.foo = 'bar'

    def upper(self, astr):
        return astr.upper()

    def lower(self, astr):
        return astr.lower()
    

class PartialMirrorManager(object):
    def __init__(self):
        self.baseparent = path('/freespace/debrepos')

    def main_list_filename(self, dist):
        basename = '%s.pkgs' % dist
        directory = self.baseparent / 'debian/conf/pkgs'
        filename = directory / basename
        return filename

    def get_selections(self, dist):
        filename = self.main_list_filename(dist)
        return selections_to_dictionary(filename, install=True)
    
        

    
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
        

    
