"""Classes for creating DNS resource records."""

__version__ = '$Revision: 1.9 $'
# $Source: /home/blb/pybind/RCS/dnsrecord.py,v $

import ipaddr

class ResourceRecord(object):

    """Base DNS resource record object."""

    def __init__(self, name, data, ttl=None, class_='IN'):
        """Return a ResourceRecord object.

        Args:
            name: (string) name of node to which this record belongs
              'host.example.com.'
            data: (string) data content of the record (varies by type)
              '192.168.1.1'
            ttl: (string or integer) time-to-live
              '1h'
            class_: (string) protocol family
              'IN'
        """

        self.name = name.strip()
        self.data = data
        self.ttl = ttl
        self.class_ = class_

    def __str__(self):
        ttl_field = '%s ' % self.ttl if self.ttl else ''
        return '%s %s%s %s %s' % (self.name, ttl_field, self.class_,
                                  self.__class__.__name__, self.data)

class SOA(ResourceRecord):

    """Start of Authority record."""

    def __init__(self, name, mname, rname, serial, refresh, retry,
                 expiry, minimum, ttl=None):
        # ensure e-mail address ends with a dot if it contains '@'
        if rname.find('@') > -1 and not rname.endswith('.'):
            rname += '.'
        rname = rname.replace('@', '.')
        data = '%s %s (%d %s %s %s %s)' % (mname, rname, serial, refresh,
                                           retry, expiry, minimum)
        super(SOA, self).__init__(name, data, ttl)

class NS(ResourceRecord):

    """Name Server record."""

    def __init__(self, name, name_server, ttl=None):
        super(NS, self).__init__(name, name_server, ttl)

class A(ResourceRecord):

    """IPv4 Address record."""

    def __init__(self, name, address, ttl=None):
        ip = ipaddr.IPv4Address(address)
        super(A, self).__init__(name, ip, ttl)

class AAAA(ResourceRecord):

    """IPv6 Address record."""

    def __init__(self, name, address, ttl=None):
        ip = ipaddr.IPv6Address(address)
        super(AAAA, self).__init__(name, ip, ttl)

class CNAME(ResourceRecord):

    """Canonical Name record."""

    def __init__(self, name, canonical_name, ttl=None):
        super(CNAME, self).__init__(name, canonical_name, ttl)

class MX(ResourceRecord):

    """Mail Exchanger record."""

    def __init__(self, name, preference, mail_exchanger, ttl=None):
        data = '%d %s' % (preference, mail_exchanger)
        super(MX, self).__init__(name, data, ttl)

class TXT(ResourceRecord):

    """Text record."""

    def __init__(self, name, text, ttl=None):
        super(TXT, self).__init__(name, '"%s"' % text, ttl)

class PTR(ResourceRecord):

    """Pointer record."""

    def __init__(self, address, name, ttl=None):
        ip = ipaddr.IPAddress(address)
        reverse = self._reverse_name(ip)
        super(PTR, self).__init__(reverse, name, ttl)

    def _reverse_name(self, ip):
        """Return IP address's FQDN in the .arpa domain."""

        if ip.version == 4:
            octets = ip.compressed.split('.')
            octets.reverse()
            return '.'.join(octets) + '.in-addr.arpa.'
        else:
            # get reversed address without colons
            digits = ip.exploded.replace(':', '')[::-1]
            # add dots
            rev = '.'.join([digits[i] for i in range(0, len(digits))])
            # return fully qualified name
            return rev + '.ip6.arpa.'

def run_tests():
    recs = []
    recs.append(SOA('@', 'ns1.example.com.', 'hostmaster@example.com.',
                    1969123100, '3h', '1h', '2d', 3600))
    recs.append(A('ns1', '192.168.1.1'))
    recs.append(MX('@', 10, 'mail.example.com.'))
    recs.append(CNAME('mailserver', 'mail'))
    recs.append(TXT('@', 'This is a text record'))
    recs.append(AAAA('@', '2001:db8::1'))
    recs.append(PTR('192.168.1.1', 'ns1.example.com.'))
    recs.append(PTR('2001:db8::1', 'ns1.example.com.'))
    for r in recs: print r

if __name__ == '__main__':
    run_tests()
