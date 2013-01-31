"""Classes for creating DNS zones and writing corresponding zone
files.

No validation is done here (e.g. requiring a SOA record) because this
module may be used to create fragments of zone files to be used via an
$INCLUDE directive. Users of this module are encouraged to employ an
external validation process like named-checkzone(8) on zone files.

Host names are passed to dnsrecord.ResourceRecord methods unmodified;
i.e. they must be terminated with a dot ('.') to be interpreted as
fully qualified domain names (FQDNs)--otherwise they will be
interpreted relative to $ORIGIN, so be diligent in minding your dots.

IP addresses may be specified in any format accepted by
ipaddr.IPAddress().

Time values may be specified either as an integer (seconds) or a
string in one of BIND's time formats.

Note that the 'name' keyword argument defaults to '@', so adding an MX
record, for example, adds an MX record for the whole domain unless
otherwise specified. The 'ttl' keyword argument defaults to None, so
records will use the zone's default time-to-live (TTL) unless
otherwise specified.
"""

import time

import ipaddr

import dnsrecord

class _Zone(object):

    """Base DNS zone object."""

    # default values for keyword args; values chosen from RFC recommendations
    TTL = '1h'
    REFRESH = '3h'
    RETRY = '1h'
    EXPIRY = '2d'
    NXDOMAIN = '1h'

    def __init__(self, origin, epochserial=False, ttl=TTL):
        """Return a _Zone object.

        Args:
            origin: (str) zone's root; '.' will be appended if necessary
              'example.com'
            epochserial: (boolean) whether to use number of seconds since
              epoch as default serial number in SOA record
            ttl: (str or int) default time-to-live for resource records
        """

        self.origin = origin
        if not self.origin.endswith('.'):
            # make sure it looks like FQDN (although it still might be wrong)
            self.origin += '.'
        self.epochserial = epochserial
        self.records = []  # list of dnsrecord objects
        self.ttl = ttl

    def write_file(self, filename):
        """Write zone file.

        Args:
            filename: (str) name of file to be written
              'zonefile.hosts'
        """

        with open(filename, 'w') as fh:
            fh.write('$ORIGIN %s\n' % self.origin)
            fh.write('$TTL %s\n' % self.ttl)
            for record in self.records:
                fh.write('%s\n' % record)
        fh.close()

    def add_record(self, record):
        """Add record to zone.

        This is abstracted from the add_*() methods in case later
        implementations store the records in a different data
        structure. (YagNi?)

        Args:
            record: (dnsrecord.ResourceRecord) record to be added
        """

        self.records.append(record)

    def add_soa(self, mname, rname, serial=None, refresh=REFRESH, retry=RETRY,
                expiry=EXPIRY, nxdomain=NXDOMAIN, name='@', ttl=None):
        """Add Start of Authority record to zone.

        Args:
            mname: (str) host name of name server authoritative for zone
              'ns1.example.com.'
            rname: (str) e-mail address of person responsible for zone
              'hostmaster@example.com'
            serial: (int) serial number
              '1969123100'
            refresh: (str or int) slave's refresh interval
            retry: (str or int) slave's retry interval
            expiry: (str or int) slave's expiry interval
            nxdomain: (str or int) negative caching time (TTL)
            name: (str) name of node to which this record belongs
              'example.com.'
        """

        if serial is None:
            # set default serial number
            if self.epochserial:
                serial = int(time.time())  # number of seconds since epoch
            else:
                serial = int(time.strftime('%Y%m%d00'))  # YYYYMMDD00
        soa = dnsrecord.SOA(name, mname, rname, serial, refresh, retry,
                            expiry, nxdomain, ttl)
        self.add_record(soa)

    def add_ns(self, name_server, name='@', ttl=None):
        """Add Name Server record to zone.

        Args:
            name_server: (str) host name of name server
              'ns1.example.com.'
            name: (str) name of node to which this record belongs
              'example.com.'
            ttl: (str or int) time-to-live
        """

        ns = dnsrecord.NS(name, name_server, ttl)
        self.add_record(ns)

class ForwardZone(_Zone):

    """Forward DNS zone."""

    def add_a(self, address, name='@', ttl=None):
        """Add IPv4 Address record to zone.

        Args:
            address: (str) IPv4 address
              '192.168.1.1'
            name: (str) name of node to which this record belongs
              'host.example.com.'
            ttl: (str or int) time-to-live
        """

        a = dnsrecord.A(name, address, ttl)
        self.add_record(a)

    def add_aaaa(self, address, name='@', ttl=None):
        """Add IPv6 Address record to zone.

        Args:
            address: (str) IPv6 address
              '2001:db8::1'
            name: (str) name of node to which this record belongs
              'host.example.com.'
            ttl: (str or int) time-to-live
        """

        aaaa = dnsrecord.AAAA(name, address, ttl)
        self.add_record(aaaa)

    def add_cname(self, canonical_name, name='@', ttl=None):
        """Add Canonical Name record to zone.

        Args:
            canonical: (str) canonical host name of host
              'mail.example.com.'
            name: (str) name of node to which this record belongs
              'mailserver.example.com.'
            ttl: (str or int) time-to-live
        """

        cname = dnsrecord.CNAME(name, canonical_name, ttl)
        self.add_record(cname)

    def add_mx(self, mail_exchanger, preference=10, name='@', ttl=None):
        """Add Mail Exchanger record to zone.

        Args:
            mail_exchanger: (str) host name of mail exchanger
              'mail.example.com.'
            preference: (int) preference value of mail exchanger
            name: (str) name of node to which this record belongs
              'example.com.'
            ttl: (str or int) time-to-live
        """

        mx = dnsrecord.MX(name, preference, mail_exchanger, ttl)
        self.add_record(mx)

    def add_txt(self, text, name='@', ttl=None):
        """Add Text record to zone.

        Args:
            text: (str) textual contents of record
              'This is a text record'
            name: (str) name of node to which this record belongs
              'example.com.'
            ttl: (str or int) time-to-live
        """

        txt = dnsrecord.TXT(name, text, ttl)
        self.add_record(txt)

class ReverseZone(_Zone):

    """Reverse DNS zone."""

    def add_ptr(self, address, name='@', ttl=None):
        """Add Pointer record to zone.

        Args:
            address: (str) IPv4 or IPv6 address
              '192.168.1.1'
            name: (str) name of node to which this record belongs
              'ns1.example.com.'
            ttl: (str or int) time-to-live
        """

        ptr = dnsrecord.PTR(address, name, ttl)
        self.add_record(ptr)

def run_tests():
    """Run rudimentary tests of module.

    These are really intended for development and debugging purposes
    rather than a substitute for unit tests.
    """

    # create forward zone and write to file
    z = ForwardZone('example.com')
    z.add_soa('ns1', 'hostmaster')
    z.add_ns('ns1')
    z.add_ns('ns2')
    z.add_mx('mail1')
    z.add_mx('mail2', 20, ttl=600)
    z.add_a('192.168.1.1', 'ns1')
    z.add_aaaa('2001:db8::1', 'ns1')
    z.add_txt('v=spf1 mx ~all')
    z.add_cname('mailserver', 'mail')
    filename = 'fwdzone'
    z.write_file(filename)
    print 'Wrote %s.' % filename

    # create IPv4 reverse zone and write to file
    z = ReverseZone('1.168.192.in-addr.arpa')
    z.add_soa('ns1.example.com.', 'hostmaster@example.com.')
    z.add_ns('ns1.example.com.')
    z.add_ptr('192.168.1.1', 'ns1.example.com.')
    filename = 'revzone4'
    z.write_file(filename)
    print 'Wrote %s.' % filename

    # create IPv6 reverse zone and write to file
    z = ReverseZone('0.0.0.0.0.0.c.f.ip6.arpa', epochserial=True)
    z.add_soa('ns1.example.com.', 'hostmaster@example.com.')
    z.add_ns('ns1.example.com.')
    z.add_ptr('2001:db8::1', 'ns1.example.com.')
    filename = 'revzone6'
    z.write_file(filename)
    print 'Wrote %s.' % filename

if __name__ == '__main__':
    run_tests()
