#!/usr/bin/env python

"""Unit tests for dnsrecord module."""

import re

import unittest2 as unittest

import dnsrecord

class TestSOA(unittest.TestCase):

    def setUp(self):
        self.mname = 'ns1.example.com.'
        self.rname = 'email@example.com'
        self.soa = dnsrecord.SOA('example.com.', self.mname,
                                 self.rname, 196912310000,
                                 '1h', '30m', '1d', '1h', 999)
        self.fields = ('mname', 'rname',
                       'serial', 'refresh', 'retry', 'expiry', 'minimum')

    def test_mname(self):
        mname = self.mname
        index = self.fields.index('mname')
        data = self.soa.data.split()
        self.assertEqual(data[index], mname)

    def test_rname(self):
        rname = self.rname.replace('@', '.') + '.'
        index = self.fields.index('rname')
        data = self.soa.data.split()
        self.assertEqual(data[index], rname)

class TestA(unittest.TestCase):

    def test_a(self):
        regex = r'host\.example\.com\s*IN\s*A\s*192\.168\.1\.1'
        a_re = re.compile(regex)
        a_rec = dnsrecord.A('host.example.com', '192.168.1.1')
        self.assertRegexpMatches(str(a_rec), a_re)

    def test_a_with_ttl(self):
        regex = r'host\.example\.com\s*666\s*IN\s*A\s*192\.168\.1\.1'
        a_re = re.compile(regex)
        a_rec = dnsrecord.A('host.example.com', '192.168.1.1', ttl=666)
        self.assertRegexpMatches(str(a_rec), a_re)

    def test_a_with_comment(self):
        regex = r'; a comment\nhost\.example\.com\s*IN\s*A\s*192\.168\.1\.1'
        a_re = re.compile(regex, re.MULTILINE)
        a_rec = dnsrecord.A('host.example.com', '192.168.1.1',
                            comment='a comment')
        self.assertRegexpMatches(str(a_rec), a_re)

    def test_a_with_multiline_comment(self):
        regex = r'''; a multi-
; line comment
host.example.com\s*IN\s*A\s*192.168.1.1'''
        a_re = re.compile(regex, re.MULTILINE)
        com = '''a multi-
line comment'''
        a_rec = dnsrecord.A('host.example.com', '192.168.1.1', comment=com)
        self.assertRegexpMatches(str(a_rec), a_re)

if __name__ == '__main__':
    unittest.main()
