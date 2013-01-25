"""Classes for writing ISC configuration files."""

__version__ = '$Revision: 1.3 $'
# $Source: /home/blb/pybind/RCS/iscconf.py,v $

def write_indent(fh, indent):
    """Write whitespace to file.

    Args:
        fh: (file) file object
        indent: (integer) number of tabs ('\t') to be written
    """

    for i in range(0, indent):
        fh.write('\t')

class _Conf(object):

    """Base class for configuration objects."""

    def __init__(self):
        self.elements = []  # list of Statement and Clause objects

    def add_element(self, element):
        """Add element to elements."""

        if not (isinstance(element, Statement) or
                isinstance(element, Clause)):
            raise TypeError('element is not a Statement or Clause')
        self.elements.append(element)

    def get_elements(self, label):
        """Return list of all elements with label from elements."""

        return [e for e in self.elements if e.label == label]

    def remove_elements(self, label):
        """Remove all elements with label from elements."""

        # modify list in situ
        self.elements[:] = [e for e in self.elements if e.label != label]

class ISCConf(_Conf):

    """Class for ISC configuration."""

    def __init__(self):
        super(ISCConf, self).__init__()

    def write_file(self, filename):
        """Write configuration to file.

        Args:
            filename: (string) path of file name to be written
        """

        with open(filename, 'w') as fh:
            for element in self.elements:
                element.write(fh)
        fh.close()

class Statement(object):

    """Class for ISC configuration statements."""

    def __init__(self, label, value=None, stanza=None):
        """Return a Statement object.

        Args:
            label: (string) type of statement
              'allow-transfer'
            value: (tuple) argument(s) for statement to be printed after label
            stanza: (tuple) argument(s) for statement to be printed in 
              a separate stanza within braces
              ('10.1.1.1', '10.1.1.2')

        This syntax allows for statements with all arguments on a single line
        as well as statements with arguments within braces ('{}').
        """

        self.label = label
        self.value = value if value else ()
        self.stanza = list(stanza) if stanza else []

    def write(self, fh, indent=0):
        """Write statement to file.

        Args:
            fh: (file) file object
            indent: (integer) number of tabs ('\t') for leading whitespace
        """

        # write label
        write_indent(fh, indent)
        fh.write('%s' % self.label)
        if self.value:
            # write items on same line
            for item in self.value:
                fh.write(' %s' % item)
        if self.stanza:
            # write a stanza with one item per line
            fh.write(' {\n');
            for item in self.stanza:
                write_indent(fh, indent + 1)
                fh.write('%s;\n' % item)
            write_indent(fh, indent)
            fh.write('};\n')
        else:
            fh.write(';\n')

class Clause(_Conf):

    """Class for ISC configuration clauses."""

    def __init__(self, label, *additional):
        """Return a Clause object.

        Args:
            label: (string) type of clause
              'view'
            additional: (tuple) additional data included between name and
              clause's opening brace
              ('example_view',)
        """

        super(Clause, self).__init__()
        self.label = label
        self.additional = additional

    def write(self, fh, indent=0):
        """Write clause to file.

        Args:
            fh: (file) file object
            indent: (integer) number of tabs ('\t') for leading whitespace
        """

        # open the clause
        write_indent(fh, indent)
        fh.write('%s' % self.label)
        for item in self.additional:
            fh.write(' %s' % item)
        fh.write(' {\n')

        # write each element to fh
        for element in self.elements:
            element.write(fh, indent + 1)

        # close the clause
        write_indent(fh, indent)
        fh.write('};\n')

def run_tests():
    c = ISCConf()

    v = Clause('view', 'example_view', 'IN')
    v.add_element(Statement('notify-source', value=('192.168.1.1',)))

    z = Clause('zone', 'example.com')
    z.add_element(Statement('also-notify', stanza=('192.168.1.2', '192.168.1.3')))
    z.add_element(Statement('type', ('master',)))
    z.add_element(Statement('file', ('"example.com.hosts"',)))
    s = Clause('server', '10.1.2.3')
    v.add_element(s)
    v.add_element(z)

    c.add_element(v)

    c.write_file('named.conf')

if __name__ == '__main__':
    run_tests()
