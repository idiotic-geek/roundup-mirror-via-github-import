#
# Copyright (c) 2001 Richard Jones
# This module is free software, and you may redistribute it and/or modify
# under the same terms as Python, so long as this copyright message and
# disclaimer are retained in their original form.
#
# This module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# $Id: test_htmltemplate.py,v 1.1 2002-01-21 11:05:48 richard Exp $ 

import unittest, cgi

from roundup.htmltemplate import TemplateFunctions
from roundup import date
from roundup.hyperdb import String, Date, Interval, Link, Multilink

class Class:
    def get(self, nodeid, attribute, default=None):
        if attribute == 'string':
            return 'Node %s: I am a string'%nodeid
        elif attribute == 'date':
            return date.Date('2000-01-01')
        elif attribute == 'interval':
            return date.Interval('-3d')
        elif attribute == 'link':
            return '1'
        elif attribute == 'multilink':
            return ['1', '2']
        elif attribute == 'key':
            return 'the key'
        elif attribute == 'html':
            return '<html>hello, I am HTML</html>'
    def list(self):
        return ['1', '2']
    def getprops(self):
        return {'string': String(), 'date': Date(), 'interval': Interval(),
            'link': Link('other'), 'multilink': Multilink('other'),
            'html': String(), 'key': String()}
    def labelprop(self):
        return 'key'

class Database:
    classes = {'other': Class()}
    def getclass(self, name):
        return Class()
    def __getattr(self, name):
        return Class()

class NodeCase(unittest.TestCase):
    def setUp(self):
        ''' Set up the harness for calling the individual tests
        '''
        self.tf = tf = TemplateFunctions()
        tf.nodeid = '1'
        tf.cl = Class()
        tf.properties = tf.cl.getprops()
        tf.db = Database()

#    def do_plain(self, property, escape=0):
    def testPlain_string(self):
        s = 'Node 1: I am a string'
        self.assertEqual(self.tf.do_plain('string'), s)

    def testPlain_html(self):
        s = '<html>hello, I am HTML</html>'
        self.assertEqual(self.tf.do_plain('html', escape=0), s)
        s = cgi.escape(s)
        self.assertEqual(self.tf.do_plain('html', escape=1), s)

    def testPlain_date(self):
        self.assertEqual(self.tf.do_plain('date'), '2000-01-01.00:00:00')

    def testPlain_interval(self):
        self.assertEqual(self.tf.do_plain('interval'), '- 3d')

    def testPlain_link(self):
        self.assertEqual(self.tf.do_plain('link'), 'the key')

    def testPlain_multilink(self):
        self.assertEqual(self.tf.do_plain('multilink'), '1, 2')


#    def do_field(self, property, size=None, height=None, showid=0):
    def testField_string(self):
        self.assertEqual(self.tf.do_field('string'),
            '<input name="string" value="Node 1: I am a string" size="30">')

    def testField_html(self):
        self.assertEqual(self.tf.do_field('html'), '<input name="html" '
            'value="&lt;html&gt;hello, I am HTML&lt;/html&gt;" size="30">')

    def testField_date(self):
        self.assertEqual(self.tf.do_field('date'),
            '<input name="date" value="2000-01-01.00:00:00" size="30">')

    def testField_interval(self):
        self.assertEqual(self.tf.do_field('interval'),
            '<input name="interval" value="- 3d" size="30">')

    def testField_link(self):
        self.assertEqual(self.tf.do_field('link'), '''<select name="link">
<option value="-1">- no selection -</option>
<option selected value="1">the key</option>
<option value="2">the key</option>
</select>''')

    def testField_multilink(self):
        self.assertEqual(self.tf.do_field('multilink'),
            '<input name="multilink" size="10" value="the key,the key">')

def suite():
   return unittest.makeSuite(NodeCase, 'test')


#
# $Log: not supported by cvs2svn $
#
#
# vim: set filetype=python ts=4 sw=4 et si
