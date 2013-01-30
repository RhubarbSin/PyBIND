"""Classes for writing BIND configuration files."""

import ipaddr

import iscconf

class BINDConf(iscconf.ISCConf):

    """Class for BIND configuration."""

    def __init__(self):
        """Return a BINDConf object."""

        super(BINDConf, self).__init__()

    def add_acl(self, acl):
        if not isinstance(acl, ACL):
            raise TypeError('%s is not an ACL' % acl)
        self.add_element(acl)

    def add_view(self, view):
        if not isinstance(view, View):
            raise TypeError('%s is not a View' % view)
        self.add_element(view)

class OptionsAndViewAndZone(object):

    """Abstract class for Options, View, and Zone classes.

    Methods defined here deal with BIND statements allowed in options,
    view, and zone clauses.
    """

    pass

class OptionsAndView(object):

    """Abstract class for Options and View classes.

    Methods defined here deal with BIND statements allowed in options
    and view clauses.
    """

    pass

class ViewAndZone(object):

    """Abstract class for View and Zone classes.

    Methods defined here deal with BIND statements allowed in view and
    zone clauses.
    """

    pass

class ACL(iscconf.Statement):

    """Class for BIND acl statement."""

    def __init__(self, acl_name, addresses, comment=None):
        """Return an ACL object.

        Args:
            acl_name: (str) ACL's name
              'example_master'
            addresses: (tuple) IP addresses in the address match list
              ('192.168.1.1', '192.168.1.2')
            comment: (str) comment to precede ACL
        """
        iscconf.Statement.__init__(self, 'acl', value=('"%s"' % acl_name,),
                                   stanza=addresses, comment=comment)

class View(iscconf.Clause):

    """Class for BIND view clause."""

    def __init__(self, view_name, class_='IN', comment=None):
        """Return a View object.

        Args:
            view_name: (str) view's name
              'example_view'
            class_: (str) view's class
              'IN'
            comment: (str) comment to precede view
        """

        iscconf.Clause.__init__(self, 'view', ('"%s"' % view_name, class_),
                                comment=comment)

    def add_zone(self, zone):
        """Add zone to view.

        Args:
            zone: (Zone) zone to be added
        """

        if not isinstance(zone, Zone):
            raise TypeError('element is not a Zone')
        self.add_element(zone)

    def set_match_destinations(self, *addresses):
        """Set view's match-destinations statement.

        Args:
            addresses: (tuple) IP addresses in the address match list
              ('192.168.1.1', '192.168.1.2')
        """

        self.remove_elements('match-destinations')
        stmt = iscconf.Statement('match-destinations', stanza=addresses)
        self.add_element(stmt)

    def set_notify_source(self, ip, port=None):
        """Set clause's notify-source or notify-source-v6 statement.

        Args:
            ip: (str) source IP address
            port: (int) source port
        """

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
        """Set clause's transfer-source or transfer-source-v6 statement.

        Args:
            ip: (str) source IP address
            port: (int) source port
        """

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
        """Return a Zone object.

        Args:
            zone_name: (str) zone's fully qualified domain name
              'example.com'
            type_: (str) zone's type
              'master'
            file_: (str) path to zone's file
              'master/example_view/example.com.hosts'
            class_: (str) zone's class
              'IN'
            comment: (str) comment to precede zone
        """

        iscconf.Clause.__init__(self, 'zone', ('"%s"' % zone_name, class_),
                                comment=comment)
        self.set_type(type_)
        self.set_file(file_)

    def set_type(self, type_):
        """Set zone's type statement.

        Args:
            type_: (str) zone's type
              'master'
        """

        self.remove_elements('type')
        stmt = iscconf.Statement('type', ('%s' % type_,))
        self.add_element(stmt)

    def set_file(self, file_):
        """Set zone's file statement.

        Args:
            file_: (str) path to zone's file
              'master/example_view/example.com.hosts'
        """

        self.remove_elements('file')
        stmt = iscconf.Statement('file', ('"%s"' % file_,))
        self.add_element(stmt)

    def set_allow_update(self, *addresses):
        """Set zone's allow-update statement.

        Args:
            addresses: (tuple) IP addresses in the address match list
              ('192.168.1.1', '192.168.1.2')
        """

        self.remove_elements('allow-update')
        stmt = iscconf.Statement('allow-update', stanza=addresses)
        self.add_element(stmt)

    def add_master(self, ip, port=None, key=None):
        """Add an IP address or ACL name to zone's masters statement.

        Args:
            ip: (str) IP address to be added
            '192.168.1.1'
        """

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
