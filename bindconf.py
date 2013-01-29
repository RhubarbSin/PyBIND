"""Classes for writing BIND configuration files."""

__version__ = '$Revision: 1.11 $'
# $Source: /home/blb/pybind/RCS/bindconf.py,v $

import ipaddr

import iscconf

class BINDConf(iscconf.ISCConf):

    """Class for BIND configuration."""

    def __init__(self):
        super(BINDConf, self).__init__()

    def add_acl(self, acl):
        if not isinstance(acl, ACL):
            raise TypeError('element is not an ACL')
        self.add_element(acl)

    def add_view(self, view):
        if not isinstance(view, View):
            raise TypeError('element is not a View')
        self.add_element(view)

class ACL(iscconf.Statement):

    """Class for BIND acl statement."""

    def __init__(self, acl_name, addresses, comment=None):
        super(ACL, self).__init__('acl', value=('"%s"' % acl_name,),
                                  stanza=addresses, comment=comment)

class View(iscconf.Clause):

    """Class for BIND view clause."""

    def __init__(self, view_name, class_='IN', comment=None):
        super(View, self).__init__('view', ('"%s"' % view_name, class_),
                                   comment=comment)

    def add_zone(self, zone):
        if not isinstance(zone, Zone):
            raise TypeError('element is not a Zone')
        self.add_element(zone)

    def set_match_destinations(self, *addresses):
        self.remove_elements('match-destinations')
        stmt = iscconf.Statement('match-destinations', stanza=addresses)
        self.add_element(stmt)

    def set_notify_source(self, ip, port=None):
        if ipaddr.IPAddress(ip).version == 4:
            label = 'notify-source'
        else:
            label = 'notify-source-v6'
        self.remove_elements(label)
        if port:
            value = (ip, 'port', port)
        else:
            value = (ip,)
        stmt = iscconf.Statement(label, value)
        self.add_element(stmt)

    def set_transfer_source(self, ip, port=None):
        if ipaddr.IPAddress(ip).version == 4:
            label = 'transfer-source'
        else:
            label = 'transfer-source-v6'
        self.remove_elements(label)
        if port:
            value = (ip, 'port', port)
        else:
            value = (ip,)
        stmt = iscconf.Statement(label, value)
        self.add_element(stmt)

class Zone(iscconf.Clause):

    """Class for BIND zone clause."""

    def __init__(self, zone_name, type_=None, file_=None, class_='IN',
                 comment=None):
        super(Zone, self).__init__('zone', ('"%s"' % zone_name, class_),
                                   comment=comment)
        self.set_type(type_)
        self.set_file(file_)

    def set_type(self, type_):
        self.remove_elements('type')
        stmt = iscconf.Statement('type', ('%s' % type_,))
        self.add_element(stmt)

    def set_file(self, file_):
        self.remove_elements('file')
        stmt = iscconf.Statement('file', ('"%s"' % file_,))
        self.add_element(stmt)

    def set_allow_update(self, *addresses):
        self.remove_elements('allow-update')
        stmt = iscconf.Statement('allow-update', stanza=addresses)
        self.add_element(stmt)

    def add_master(self, ip, port=None, key=None):
        # supports only IP addresses and not masters lists
        master = ip
        if port:
            master += ' port %s' % port
        if key:
            master += ' key %s' % key
        try:
            # get existing masters statement
            stmt = self.get_elements('masters')[0]
        except IndexError:
            # make new masters statement
            stmt = iscconf.Statement('masters')
            self.add_element(stmt)
        finally:
            stmt.stanza.append(master)

class NotImplemented(object):

    """Class for BIND clauses/statements not implemented yet."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError

class Controls(NotImplemented): pass
class Include(NotImplemented): pass
class Key(NotImplemented): pass
class Logging(NotImplemented): pass
class LWRes(NotImplemented): pass
class Options(NotImplemented): pass
class Server(NotImplemented): pass
class TrustedKeys(NotImplemented): pass

def run_tests():
    c = BINDConf()
    a = ACL('example_acl', ('1.1.1.1', '2.2.2.2'))
    c.add_acl(a)
    v = View('example_view')
    c.add_view(v)
    z = Zone('example.com', 'master', 'example.com.hosts',
             comment='This is a comment')
    z.set_allow_update('none')
    z.add_master('1.2.3.4')
    z.add_master('1.2.3.5', 5353)
    v.add_zone(z)
    v.set_match_destinations('1.1.1.1', '2.2.2.2')
    v.set_notify_source('3.3.3.3')
    v.set_comment('view comment')

    # v.add_element(Statement('notify-source', '192.168.1.1'))

    # z = Clause('zone', 'example.com')
    # z.add_element(Statement('also-notify', ('192.168.1.2', '192.168.1.3')))
    # z.add_element(Statement('type', 'master'))
    # z.add_element(Statement('file', '"example.com.hosts"'))
    # s = Clause('server', '10.1.2.3')
    # v.add_element(s)
    # v.add_element(z)

    # c.add_element(v)

    c.write_file('named.conf')

if __name__ == '__main__':
    run_tests()
