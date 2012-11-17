#!/usr/bin/python2.6
"""
Classes for writing BIND configuration files.

Some current limitations:
 - does not perform validation of the objects it creates; use
   named-checkconf(8) on the output file.
 - explicitly supports only view and zone clauses.
"""

__version__ = '$Revision: 1.5 $'
# $Source: /home/blb/bindtools/RCS/bindconfig.py,v $

class clauselist(list):
    """Subclass of list.

    This differs from list in name only to facilitate distinguishing a list
    of Clauses from a list of strings. A string can be written via
    file.write(), but a Clause must be written via Clause.write().
    """

    def __init__(self, iterable=None):
        super(clauselist, self).__init__(iterable if iterable else [])

class BINDConfig(object):
    """Class for BIND configuration.

    Contains a list of Clause instances.
    """

    def __init__(self, statements=None, clauses=None):
        super(BINDConfig, self).__init__()
        self.clauses = clauselist(clauses)

    def add_clause(self, clause):
        self.clauses.append(clause)

    def write_file(self, filename):
        with open(filename, 'w') as fh:
            for clause in self.clauses:
                clause.write(fh)
        fh.close()

class Clause(object):
    """Base class for BIND configuration clauses.

    Every attribute is a string, list, clauselist, or Clause.

    Where ipaddr appears, an ACL name could be passed if port is not
    specified, but this code does not explicitly support ACLs.
    """

    def __init__(self, name, clauses=None):
        super(Clause, self).__init__()
        self.name = name
        self.clauses = clauselist(clauses)

    def add_clause(self, clause):
        self.clauses.append(clause)

    def write(self, fh, indent=0):
        """Write this clause to fh with indent tabs as leading whitespace."""

        # open the clause
        self._write_indent(fh, indent)
        self._write_name(fh)

        # write each attribute to fh
        for attr in self.__dict__.iterkeys():
            if attr == 'name':  # handled by _write_name()
                continue
            obj = getattr(self, attr)

            if type(obj) is str:
                statement = attr.replace('_', '-')
                self._write_indent(fh, indent + 1)
                fh.write('%s %s;\n' % (statement, obj))

            elif type(obj) is list and len(obj) > 0:
                statement = attr.replace('_', '-')
                self._write_indent(fh, indent + 1)
                fh.write('%s {\n' % statement)
                for item in obj:
                    self._write_indent(fh, indent + 2)
                    fh.write('%s;\n' % item)
                self._write_indent(fh, indent + 1)
                fh.write('};\n')

            elif type(obj) is clauselist and len(obj) > 0:
                for clause in obj:
                    clause.write(fh, indent + 1)

            elif type(obj) is Clause:
                obj.write(fh, indent + 1)

        # close the clause
        self._write_indent(fh, indent)
        fh.write('};\n')

    def _write_name(self, fh):
        # write opening of clause to fh
        type_ = type(self).__name__.lower().replace('clause', '')
        fh.write('%s "%s" {\n' % (type_, self.name))

    def _write_indent(self, fh, indent):
        # write indent tabs to fh
        for i in range(0, indent):
            fh.write('\t')

class ViewClause(Clause):
    """Class for BIND view clauses.

    Contains several string and list attributes and a list of
    ZoneClause instances.
    """

    def __init__(self, name, notify_source=None, transfer_source=None,
                 match_destinations=None, clauses=None):
        super(ViewClause, self).__init__(name, clauses)
        self.notify_source = notify_source
        self.transfer_source = transfer_source
        self.match_destinations = (match_destinations if match_destinations
                                   else [])

    def add_match_destinations(self, ipaddr):
        self.match_destinations.append(ipaddr)

    def set_notify_source(self, ipaddr):
        self.notify_source = ipaddr

    def set_transfer_source(self, ipaddr):
        self.transfer_source = ipaddr

    def add_zone(self, zone):
        self.add_clause(zone)
        # self.clauses.append(zone)

class ZoneClause(Clause):
    """Class for BIND zone clauses.

    Contains several string and list attributes.
    """

    def __init__(self, name, type_=None, file_=None, notify=None,
                 masters=None, allow_update=None, also_notify=None):
        super(ZoneClause, self).__init__(name)
        self.type = type_
        self.file = file_
        self.notify = notify
        self.masters = masters if masters else []
        self.allow_update = allow_update if allow_update else []
        self.also_notify = also_notify if also_notify else []

    def set_type(self, type_):
        self.type = type_

    def set_file(self, file_):
        self.file = '"%s"' % file_  # file name must be quoted

    def add_master(self, ipaddr, port=None):
        if port is None:
            self.masters.append(ipaddr)
        else:
            self.also_notify.append('%s port %d' % (ipaddr, int(port)))

    def add_allow_update(self, ipaddr):
        self.allow_update.append(ipaddr)

    def set_notify(self, behavior):
        self.notify = behavior

    def add_also_notify(self, ipaddr, port=None):
        if port is None:
            self.also_notify.append(ipaddr)
        else:
            self.also_notify.append('%s port %d' % (ipaddr, int(port)))

def run_tests():
    b = BINDConfig()
    v = ViewClause('foo.com', notify_source='1.1.1.1')

    z = ZoneClause('foo.com')
    z.set_type('master')
    z.set_file('masters/foo.com')
    z.add_allow_update('none')
    z.set_notify('explicit')
    z.add_also_notify('1.1.1.2', 5053)
    v.add_zone(z)

    z = ZoneClause('bar.com',
                   type_='master',
                   file_='"masters/bar.com"',
                   allow_update=['none'],
                   notify='explicit',
                   also_notify=['1.1.1.2 port 5053'])
    v.add_zone(z)

    z = ZoneClause('foo.net')
    z.set_type('slave')
    z.set_file('slaves/foo.net')
    z.add_master('1.1.1.2')
    v.add_zone(z)

    b.add_clause(v)
    b.write_file('test')
    print 'Wrote test.'

if __name__ == '__main__':
    run_tests()
