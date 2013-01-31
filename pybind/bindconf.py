"""Classes for writing BIND configuration files.

This module does not prevent the creation of invalid configuration
files. Any use must account for restrictions and requirements in
named.conf as specified by the official documentation. Here are some
examples:

- Definitions must be properly ordered; e.g. access control lists and
  masters lists must be defined before references to them.

- Some statements are disallowed based on context; e.g. a zone
  definition of type "master" is not allowed to have a "masters"
  statement.

Some restrictions are enforced here (e.g. you can't define an ACL
within a view clause), but don't count on them to guarantee a working
configuration. After all, "BIND allows a daunting list of
configuration entities."
"""

import ipaddr

import iscconf

class BINDConf(iscconf.ISCConf):

    """Class for BIND configuration."""

    def __init__(self):
        """Return a BINDConf object."""

        iscconf.ISCConf.__init__(self)

    def add_acl(self, acl):
        """Add an acl statement.

        Args:
            acl: (ACL) ACL object to be added
        """

        if not isinstance(acl, ACL):
            raise TypeError('%s is not an ACL' % acl)
        self.add_element(acl)

    def add_named_masters(self, named_masters):
        """Add a named masters clause.

        Args:
            named_masters: (NamedMasters) NamedMasters object to be added
        """

        if not isinstance(named_masters, NamedMasters):
            raise TypeError('%s is not a NamedMasters' % named_masters)
        self.add_element(named_masters)

    def add_view(self, view):
        """Add a view clause.

        Args:
            view: (View) View object to be added
        """

        if not isinstance(view, View):
            raise TypeError('%s is not a View' % view)
        self.add_element(view)

class _OptionsAndViewAndZone(object):

    """Abstract class for Options, View, and Zone classes.

    Methods defined here deal with BIND statements allowed in options,
    view, and zone clauses.
    """

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

class _OptionsAndView(object):

    """Abstract class for Options and View classes.

    Methods defined here deal with BIND statements allowed in options
    and view clauses.
    """

    pass

class _ViewAndZone(object):

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
              'example_acl'
            addresses: (tuple) IP addresses in the address match list
              ('192.168.1.1', '192.168.1.2')
            comment: (str) comment to precede ACL
        """

        # It could be argued this should be a Clause instead of a
        # Statement, as some reference material refers to it as such,
        # but the syntax is accomodated by the definition of Statement
        # in iscconf.
        iscconf.Statement.__init__(self, 'acl', value=('"%s"' % acl_name,),
                                   stanza=addresses, comment=comment)

class _Masters(object):

    """Abstract class for NamedMasters and Masters classes."""

    def add_masters_name(self, masters_name):
        """Add the name of a named masters clause to masters list.

        Args:
            masters_name: (str) name of masters list to be added
              'example_masters'
        """

        stmt = iscconf.Statement(masters_name)
        self.add_element(stmt)

    def add_master(self, master, port=None, key=None):
        """Add an IP address to masters list.

        Args:
            master: (str) IP address or name of masters list to be added
              '192.168.1.1'
            port: (int) port for IP address
            key: (str) authentication key for IP address
        """

        ip = ipaddr.IPAddress(master)
        value = []
        if port:
            value.extend(['port', port])
        if key:
            value.extend(['key', '"%s"' % key])
        stmt = iscconf.Statement(str(ip), value=tuple(value))
        self.add_element(stmt)

class NamedMasters(iscconf.Clause, _Masters):

    """Class for named BIND masters clause.

    This is different from a Masters object because it has a name and
    is allowed only in the global context (as an element of a BINDConf
    object).
    """

    def __init__(self, masters_name, port=None, comment=None):
        """Return a NamedMasters object.

        Args:
            masters_name: (str) masters statement's name
              'example_masters'
            port: (int) port number for all addresses in clause
            comment: (str) comment to precede masters statement
        """

        additional = [masters_name]
        if port:
            additional.extend(['port', port])
        iscconf.Clause.__init__(self, 'masters', tuple(additional),
                                comment=comment)

class Masters(iscconf.Clause, _Masters):

    """Class for BIND masters clause in a slave zone.

    This is different from a NamedMasters object because it has no
    name and is allowed only in the zone context (as an element of a
    Zone object).
    """

    def __init__(self, port=None, comment=None):
        """Return a Masters object.

        Args:
            port: (int) port number for all addresses in clause
            comment: (str) comment to precede masters statement
        """

        additional = ('port', port) if port else None
        iscconf.Clause.__init__(self, 'masters', additional, comment=comment)

class View(iscconf.Clause, _OptionsAndViewAndZone, _OptionsAndView,
           _ViewAndZone):

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

class Zone(iscconf.Clause, _OptionsAndViewAndZone, _ViewAndZone):

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

    def set_masters(self, masters):
        """Set zone's masters clause.

        Args:
            masters: (Masters) Masters object
        """

        self.remove_elements('masters')
        self.add_element(masters)

class _NotImplemented(object):

    """Class for BIND clauses/statements not implemented yet."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError

class Controls(_NotImplemented): pass
class Include(_NotImplemented): pass
class Key(_NotImplemented): pass
class Logging(_NotImplemented): pass
class LWRes(_NotImplemented): pass
class Options(_NotImplemented, _OptionsAndViewAndZone, _OptionsAndView): pass
class Server(_NotImplemented): pass
class TrustedKeys(_NotImplemented): pass

def run_tests():
    c = BINDConf()
    a = ACL('example_acl', ('1.1.1.1', '2.2.2.2'))
    c.add_acl(a)
    # m = Masters('example_masters', ('3.3.3.3', '4.4.4.4'), comment='a comment')
    # c.add_masters(m)
    v = View('example_view')
    c.add_view(v)
    z = Zone('example.com', 'slave', 'example.com.hosts',
             comment='This is a comment')
    # z.set_allow_update('none')
    # z.add_master('example_masters')
    # z.add_master('1.2.3.4')
    # z.add_master('1.2.3.5', 5353)
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
