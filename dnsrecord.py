"""Classes for creating DNS resource records."""

__version__ = '$Revision: 1.3 $'
# $Source: /home/blb/pybind/RCS/dnsrecord.py,v $

import ipaddr

class ResourceRecord(object):

    """Base DNS resource record object."""

    def __init__(self, name, data, ttl=None, class_='IN'):
        self.name = name.strip()
        self.data = data
        self.ttl = ttl
        self.class_ = class_

    def __str__(self):
        ttl_str = '%s ' % self.ttl if self.ttl else ''
        return '%s %s%s %s %s' % (self.name, ttl_str, self.class_,
                                  self.__class__.__name__, self.data)

class SOA(ResourceRecord):

    def __init__(self, name, mname, rname, serial, refresh, retry,
                 expiry, minimum, ttl=None):
        rname = rname.replace('@', '.')
        data = '%s %s (%d %s %s %s %s)' % (mname, rname, serial,
                                           str(refresh), str(retry),
                                           str(expiry), str(minimum))
        super(SOA, self).__init__(name, data, ttl)

class NS(ResourceRecord):

    def __init__(self, name, name_server, ttl=None):
        super(NS, self).__init__(name, name_server, ttl)

class A(ResourceRecord):

    def __init__(self, name, address, ttl=None):
        ip = ipaddr.IPv4Address(address)
        super(A, self).__init__(name, ip, ttl)

class AAAA(ResourceRecord):

    def __init__(self, name, address, ttl=None):
        ip = ipaddr.IPv6Address(address)
        super(AAAA, self).__init__(name, ip, ttl)

class CNAME(ResourceRecord):

    def __init__(self, name, canonical_name, ttl=None):
        super(CNAME, self).__init__(name, canonical_name, ttl)

class MX(ResourceRecord):

    def __init__(self, name, preference, mail_exchanger, ttl=None):
        data = '%d %s' % (preference, mail_exchanger)
        super(MX, self).__init__(name, data, ttl)

class TXT(ResourceRecord):

    def __init__(self, name, text, ttl=None):
        super(TXT, self).__init__(name, '"%s"' % text, ttl)

class PTR(ResourceRecord):

    def __init__(self, address, name, ttl=None):
        ip = ipaddr.IPAddress(address)
        reverse = self._reverse_name(ip)
        super(PTR, self).__init__(reverse, name, ttl)

    def _reverse_name(self, ip):
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

if __name__ == '__main__':
    recs = []
    recs.append(SOA('@', 'ns1.foo.com.', 'foo.foo.com.', 1969123100,
                    14400, 3600, 86400, 600, '1d'))
    recs.append(A('mail', '1.1.1.1'))
    recs.append(MX('@', 25, 'mail.foo.com.'))
    recs.append(CNAME('www', 'mail'))
    recs.append(TXT('@', 'some text'))
    recs.append(AAAA('@', 'c0ff::ee00'))
    recs.append(PTR('1.2.3.4', 'mail.bar.com.'))
    recs.append(PTR('abcd:ef12::4321', 'mail.bar.com.'))
    for r in recs: print r
