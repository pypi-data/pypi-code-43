# coding: utf-8
#  -*- Mode: Python; -*-                                              
#
# python test.py [local | system]
#  AUTHOR Jenna N. Shockley
#  AUTHOR Jamie A. Jennings

# TODO:
# - replace magic error code numbers with constants
# python test.py [local | system]
#
from __future__ import unicode_literals, print_function

import unittest
import sys, os, json
import rosie

# Notes
#
# (1) We use the librosie.so that is in the directory above this one,
#     i.e. "..", so we supply the librosiedir argument to
#     rosie.engine().  Normally, no argument to rosie.engine() is
#     needed.

if sys.version_info.major < 3:
    str23 = lambda s: str(s)
    bytes23 = lambda s: bytes(s)
else:
    str23 = lambda s: str(s, encoding='UTF-8')
    bytes23 = lambda s: bytes(s, encoding='UTF-8')

# -----------------------------------------------------------------------------
# Tests for Engine class
# -----------------------------------------------------------------------------

class RosieEngineTest(unittest.TestCase):

    def setUp(self):
        rosie.load(librosiedir, quiet=True)
        self.engine = rosie.engine()
        pass

    def tearDown(self):
        pass

    def testInit(self):
        assert(self.engine)
        path = rosie.librosie_path()
        assert(path)

    def testLoad(self):
        try:
            pkgname = self.engine.load(b'package x; foo = "foo"')
            self.assertTrue(pkgname == b"x")
        except RuntimeError:
            self.fail()

        try:
            b = self.engine.compile(b"x.foo")
            self.assertTrue(b.valid())
        except RuntimeError:
            self.fail()

        try:
            bb = self.engine.compile(b"[:digit:]+")
            self.assertTrue(bb.valid())
        except RuntimeError:
            self.fail()

        b2 = None
        try:
            b2 = self.engine.compile(b"[:foobar:]+")
            self.fail()
        except RuntimeError as e:
            self.assertTrue(not b2)
            self.assertTrue(str(e))
            #todo fix
            #self.assertEqual(str(e), "RPL error:\nb\'[{\"who\":\"compiler\",\"formatted\":\"Compile error\\n\\t[compiler]: unknown named charset: foobar\\n\\tin user input :1:3: [:foobar:]+\",\"message\":\"unknown named charset: foobar\"}]\'")

        try:
            b = None                       # trigger call to librosie to gc the compiled pattern
            b = self.engine.compile(b"[:digit:]+")
        except RuntimeError:
            self.fail()

        num_int = None
        try:
            num_int = self.engine.compile(b"num.int")
            self.fail()
        except RuntimeError as e:
            self.assertTrue(not num_int)
            self.assertTrue(str(e))
            #todo fix
            self.assertEqual(str(e), str(e))

        try:
            pkgname = self.engine.load(b'foo = "')
            self.fail()
        except RuntimeError as e:
            self.assertTrue(str(e))
            #todo fix
            self.assertEqual(str(e), str(e))

        engine2 = rosie.engine()
        self.assertTrue(engine2)
        self.assertTrue(engine2 != self.engine)
        engine2 = None          # triggers call to librosie to gc the engine

    def testConfig(self):
        cfg = self.engine.config()
        self.assertTrue(cfg)
        array = cfg[0]
        for entry in array:
            self.assertTrue(type(entry) is dict)
            self.assertTrue(entry['name'])
            self.assertTrue(entry['description'])
            if not entry['value']:
                self.assertTrue(entry['name'] == 'ROSIE_COMMAND')
        array = cfg[1]
        rpl_version = None
        libpath = None
        for entry in array:
            if entry['name']=='RPL_VERSION':
                rpl_version = entry['value']
            if entry['name']=='ROSIE_LIBPATH':
                libpath = entry['value']
        if sys.version_info.major < 3:
            self.assertTrue(type(rpl_version) is unicode)
            self.assertTrue(type(libpath) is unicode)
        else:
            self.assertTrue(type(rpl_version) is str)
            self.assertTrue(type(libpath) is str)

    def testLibpath(self):
        path = self.engine.libpath()
        self.assertIsInstance(path, bytes)
        newpath = b"foo bar baz"
        self.engine.libpath(newpath)
        testpath = self.engine.libpath()
        self.assertIsInstance(testpath, bytes)
        self.assertTrue(testpath == newpath)
        
    def testAllocLimit(self):
        limit, usage = self.engine.alloc_limit()
        self.assertIsInstance(limit, int)
        self.assertTrue(limit == 0)
        limit, usage = self.engine.alloc_limit(0)
        limit, usage = self.engine.alloc_limit()
        self.assertTrue(limit == 0)
        limit, usage = self.engine.alloc_limit(8199)
        self.assertTrue(limit == 8199)
        with self.assertRaises(ValueError):
            limit, usage = self.engine.alloc_limit(8191) # too low
        limit, usage = self.engine.alloc_limit()
        self.assertTrue(limit == 8199)
            
    def testImport(self):
        try:
            pkgname = self.engine.import_package(b'net')
            self.assertTrue(pkgname == b'net')
        except RuntimeError:
            self.fail()

        try:
            pkgname = self.engine.import_package(b'net', b'foobar')
            self.assertTrue(pkgname == b'net') # actual name inside the package
        except RuntimeError:
            self.fail()

        net_any = None
        try:
            net_any = self.engine.compile(b"net.any")
            self.assertTrue(net_any)
        except RuntimeError:
            self.fail()

        try:
            foobar_any = self.engine.compile(b"foobar.any")
            self.assertTrue(foobar_any)
        except RuntimeError:
            self.fail()
        
        m = net_any.match(b"1.2.3.4", 1, encoder = b"color")
        self.assertTrue(m)
        m = net_any.match(b"Hello, world!", 1, encoder = b"color")
        self.assertTrue(not m)

        try:
            pkgname = self.engine.import_package(b'THISPACKAGEDOESNOTEXIST')
        except RuntimeError as e:
            self.assertTrue(e)
    
    def testLoadFile(self):
        try:
            pkgname = self.engine.loadfile(b'test.rpl')
            self.assertTrue(pkgname == bytes(b'test'))
        except RuntimeError:
            self.fail()

    def testMatch(self):
        # test short match
        try:
            m = self.engine.match(b"[:digit:]+", b"321")
            self.assertTrue(m)
            self.assertTrue(m.start() == 1)     # match started at char 2
            self.assertTrue(m.end() == 4)
            self.assertTrue(m.group() == "321")
            self.assertTrue(m.abend() == False)
        except:
            self.fail()

        # test no match
        try:
            m = self.engine.match(b"[:digit:]+", b"xyz")
            self.assertTrue(m == None)
        except:
            self.fail()

        # test long match
        inp = b"889900112233445566778899100101102103104105106107108109110xyz"
        linp = len(inp)

        try:
            m = self.engine.match(b"[:digit:]+", inp)
            self.assertTrue(m)
            self.assertTrue(m.start() == 1)
            self.assertTrue(m.end() == linp-3+1) # due to the "xyz" at the end
            self.assertTrue(m.group() == str23(inp[0:-3]))
            self.assertTrue(m.abend() == False)
        except:
            self.fail()

    def testFullMatch(self):
        try:
            pkgname = self.engine.load(b'package year; d = [0-9]')
        except:
            self.fail()

        m = self.engine.fullmatch(b'year.d{4}', b"1998")
        self.assertTrue(m)
        self.assertEqual(m.group(), "1998")

        m = self.engine.fullmatch(b'year.d{4}', b"1998 Year")
        self.assertTrue(m == None)

    def testTrace(self):
        pkgname = self.engine.import_package(b'net')
        self.assertTrue(pkgname)

        dict = self.engine.trace(b'net.fqdn_strict', b"a.b.c", encoder=b"condensed")
        self.assertTrue(dict['matched'] == True)
        self.assertTrue(dict['trace'])
        self.assertTrue(len(dict['trace']) > 0)

        dict = self.engine.trace(b"net.fqdn_strict", b"a.b.c", encoder=b"condensed")
        self.assertTrue(dict['matched'] == True)
        self.assertTrue(dict['trace'])
        self.assertTrue(len(dict['trace']) > 0)

        dict = self.engine.trace(b'net.fqdn_strict', b"a.b.c", encoder=b"full")
        self.assertTrue(dict['matched'] == True)
        self.assertTrue(dict['trace'])
        self.assertTrue(len(dict['trace']) > 0)
        self.assertTrue(dict['trace'].find(b'Matched 5 chars') != -1)

        try:
            dict = self.engine.trace(b'net.fqdn_strict', b"a.b.c", encoder=b"no_such_trace_style")
            # force a failure in case the previous line does not throw an exception:
            self.assertTrue(False)
        except ValueError as e:
            self.assertTrue(repr(e).find('invalid trace style') != -1)

        trace_object = self.engine.trace(b'net.fqdn_strict', b"a.b.c")
        self.assertTrue(trace_object.trace_value())
        self.assertTrue(len(trace_object.trace_value()) > 0)
        self.assertTrue('match' in trace_object.trace_value())
        self.assertTrue(trace_object.trace_value()['match'])
        self.assertTrue('nextpos' in trace_object.trace_value())
        self.assertTrue(trace_object.trace_value()['nextpos'] == 6)
    
    def testSearch(self):
        try:
            pkgname = self.engine.load(b'package year; d = [0-9]')
        except:
            self.fail()

        m = self.engine.search('year.d{4}', "info 1998 23 2006 time 1876")
        self.assertEqual(m.group(), "1998")

    def testFindall(self):
        try:
            pkgname = self.engine.load(b'package year; d = [0-9]')
        except:
            self.fail()

        matches = self.engine.findall('year.d{4}', "info 1998 23 2006 time 1876")
        self.assertTrue("1998" in matches)
        self.assertTrue("2006" in matches)
        self.assertTrue("1876" in matches)
        self.assertTrue("23" not in matches)

    def testSub(self):
        self.assertEqual(self.engine.sub('[0-9]{4}', 'time', 'the year of 1956 and 1957'), 'the year of time and time')

    def testSubn(self):
        self.assertEqual(self.engine.subn('[0-9]{4}', 'time', 'the year of 1956 and 1957'), ('the year of time and time', 2))

    def testReadRCFile(self):
        if testdir:
            options, messages = self.engine.read_rcfile(bytes23(os.path.join(testdir, "rcfile1")))
            self.assertIsInstance(options, list)
            self.assertTrue(messages is None)
            options, messages = self.engine.read_rcfile(bytes23(os.path.join(testdir, "rcfile2")))
            self.assertTrue(messages[0].find("Syntax errors in rcfile") != -1)
            self.assertTrue(options is False)
            options, messages = self.engine.read_rcfile(b"This file does not exist")
            self.assertTrue(options is None)
            self.assertTrue(messages[0].find("Could not open rcfile") != -1)
            
    def testExecuteRCFile(self):
        result, messages = self.engine.execute_rcfile(b"This file does not exist")
        self.assertTrue(result is None)
        if testdir:
            result, messages = self.engine.execute_rcfile(bytes23(os.path.join(testdir, "rcfile1")))
            self.assertFalse(result)
            self.assertTrue(messages[0].find("Failed to load another-file") != -1)
            result, messages = self.engine.execute_rcfile(bytes23(os.path.join(testdir, "rcfile2")))
            self.assertFalse(result)
            self.assertTrue(messages[0].find("Syntax errors in rcfile") != -1)
            result, messages = self.engine.execute_rcfile(bytes23(os.path.join(testdir, "rcfile3")))
            self.assertFalse(result)
            self.assertTrue(messages[0].find("Failed to load nofile_mod1.rpl") != -1)
            result, messages = self.engine.execute_rcfile(bytes23(os.path.join(testdir, "rcfile6")))
            self.assertTrue(result)
            self.assertTrue(messages is None)

    def testDeps(self):
        # Expression
        result, messages = self.engine.expression_deps(b"A")
        self.assertFalse(result is None)
        self.assertTrue(messages is None)
        pt = json.loads(result)
        self.assertTrue(len(pt) == 0)
        result, messages = self.engine.expression_deps(b'A / "hello" / B.c [:digit:]+ p.mac:#hi')
        def check_deps(result, messages, index=None):
            self.assertFalse(result is None)
            self.assertTrue(messages is None)
            pt = json.loads(result)
            if index: pt = pt[index]
            self.assertTrue(len(pt) == 2)
            self.assertTrue(pt[0] == 'B')
            self.assertTrue(pt[1] == 'p')
        check_deps(result, messages)
        result, messages = self.engine.expression_deps(b"A // B.c") # syntax error
        self.assertTrue(result is None)
        self.assertFalse(messages is None)
        # Block
        result, messages = self.engine.block_deps(b"x = A / B.c; y=[:alpha:] p.mac:#tagname")
        check_deps(result, messages, 'implicit')
        result, messages = self.engine.block_deps(b"import F as G, H; x = A / B.c; y=[:alpha:] p.mac:#tagname")
        check_deps(result, messages, 'implicit')
        pt = json.loads(result)
        pt = pt['explicit']
        self.assertTrue(len(pt) == 2)
        self.assertTrue('as_name' in pt[0])
        self.assertTrue(pt[0]['as_name'] == 'G')
        self.assertTrue('importpath' in pt[0])
        self.assertTrue(pt[0]['importpath'] == 'F')
        self.assertTrue(not 'as_name' in pt[1])
        self.assertTrue('importpath' in pt[1])
        self.assertTrue(pt[1]['importpath'] == 'H')
        result, messages = self.engine.block_deps(b" = A / B.c; y=[:alpha:]") # syntax error
        self.assertTrue(result is None)
        self.assertFalse(messages is None)

    def testRefs(self):
        # Expression
        result, messages = self.engine.expression_refs(b"A")
        self.assertFalse(result is None)
        self.assertTrue(messages is None)
        pt = json.loads(result)
        self.assertTrue(len(pt) == 1)
        self.assertTrue('ref' in pt[0])
        self.assertTrue('localname' in pt[0]['ref'])
        self.assertTrue(pt[0]['ref']['localname'] == "A")
        result, messages = self.engine.expression_refs(b'A / "hello" / B.c [:digit:]+ mac:#hi')
        def check_refs(result, messages):
            self.assertFalse(result is None)
            self.assertTrue(messages is None)
            pt = json.loads(result)
            self.assertTrue(len(pt) == 3)
            self.assertTrue('ref' in pt[0])
            self.assertTrue(pt[0]['ref']['localname'] == "A")
            self.assertTrue('ref' in pt[1])
            self.assertTrue(pt[1]['ref']['packagename'] == "B")
            self.assertTrue(pt[1]['ref']['localname'] == "c")
            self.assertTrue('ref' in pt[2])
            self.assertTrue(pt[2]['ref']['localname'] == "mac")
        check_refs(result, messages)
        result, messages = self.engine.expression_refs(b"A // B.c") # syntax error
        self.assertTrue(result is None)
        self.assertFalse(messages is None)
        # Block
        result, messages = self.engine.block_refs(b"x = A / B.c; y=[:alpha:] mac:#tagname")
        check_refs(result, messages)
        result, messages = self.engine.block_refs(b" = A / B.c; y=[:alpha:]") # syntax error
        self.assertTrue(result is None)
        self.assertFalse(messages is None)

    def testParse(self):
        # Parse expression
        result, messages = self.engine.parse_expression(b"A")
        self.assertFalse(result is None)
        self.assertTrue(messages is None)
        pt = json.loads(result)
        self.assertTrue('ref' in pt)
        self.assertTrue('localname' in pt['ref'])
        self.assertTrue(pt['ref']['localname'] == "A")
        result, messages = self.engine.parse_expression(b"A / B.c")
        self.assertFalse(result is None)
        self.assertTrue(messages is None)
        pt = json.loads(result)
        self.assertTrue('choice' in pt)
        self.assertTrue('exps' in pt['choice'])
        second_exp = pt['choice']['exps'][1]
        self.assertTrue('ref' in second_exp)
        self.assertTrue(second_exp['ref']['packagename'] == "B")
        self.assertTrue(second_exp['ref']['localname'] == "c")
        result, messages = self.engine.parse_expression(b"A // B.c") # syntax error
        self.assertTrue(result is None)
        self.assertFalse(messages is None)
        # Parse block
        result, messages = self.engine.parse_block(b"x = A / B.c; y=[:alpha:]")
        self.assertFalse(result is None)
        self.assertTrue(messages is None)
        pt = json.loads(result)
        self.assertTrue('block' in pt)
        self.assertTrue('stmts' in pt['block'])
        binding1 = pt['block']['stmts'][0]
        binding2 = pt['block']['stmts'][1]
        def check_binding(b, boundname):
            self.assertTrue('binding' in b)
            self.assertTrue('ref' in b['binding'])
            self.assertTrue('ref' in b['binding']['ref'])
            self.assertTrue('localname' in b['binding']['ref']['ref'])
            self.assertTrue(b['binding']['ref']['ref']['localname'] == boundname)
        check_binding(binding1, 'x')
        check_binding(binding2, 'y')
        result, messages = self.engine.parse_block(b" = A / B.c; y=[:alpha:]") # syntax error
        self.assertTrue(result is None)
        self.assertFalse(messages is None)

# -----------------------------------------------------------------------------
# Tests for RPLX class
# -----------------------------------------------------------------------------

class RosieRPLXTest(unittest.TestCase):

    engine = None
    
    def setUp(self):
        rosie.load(librosiedir, quiet=True)
        self.engine = rosie.engine()

    def tearDown(self):
        pass

    def test_match_object(self):
        b = None
        try:
            pkgname = self.engine.load(b'package email; x1 = [a-z]+; x2 = [a-z]+; x3 = [a-z]+')
            b = self.engine.compile(b'email.x1[@]email.x2[.]email.x3')
            self.assertTrue(b.valid())
        except:
            self.fail()

        m = b.match(b"user@ncsu.edu")
        self.assertTrue(m)
        self.assertTrue(m.start() == 1)     # match started at char 1
        self.assertEqual(m.end(), 14)
        self.assertEqual(m.group(), "user@ncsu.edu")
        self.assertEqual(m.groupdict(), {'*': 'user@ncsu.edu', 'x1': 'user', 'x2': 'ncsu', 'x3': 'edu'})
        self.assertEqual(m.group('x1', 'x2'), ("user", "ncsu"))
        self.assertEqual(m.group('x1'), "user")
        self.assertEqual(m['x1'], "user")
        self.assertEqual(m.start('x1'), 1)
        self.assertEqual(m.subs('x1'), ['user'])
        self.assertEqual(m.start(1), 1)
        self.assertEqual(m.end('x1'), 5)
        self.assertEqual(m.end(1), 5)
        self.assertEqual(m.span('x1'), (1,5))
        self.assertEqual(m.lastindex(), 3)
        self.assertEqual(m.lastgroup(), 'x3')
        self.assertEqual(m.group(0), "user@ncsu.edu")
        self.assertEqual(m.group(1), "user")
        self.assertEqual(m.group(2), "ncsu")
        self.assertEqual(m[2], "ncsu")
        self.assertEqual(m.group(3), "edu")
        self.assertEqual(m.group(1,2,3), ('user', 'ncsu', 'edu'))
        self.assertTrue(m.abend() == False)

        self.assertEqual(m.expand(r"hello \1 is done"), "hello user is done")
        self.assertEqual(m.expand(r'\1 is done'), "user is done")
        self.assertEqual(m.expand(r'username: \1 email: \2 end: \3'), "username: user email: ncsu end: edu")
        self.assertEqual(m.expand(r'username: \g<1> email: \g<2> end: \g<3>'), "username: user email: ncsu end: edu")
        self.assertEqual(m.expand(r'username: \g<x1> email: \g<x2> end: \g<x3>'), "username: user email: ncsu end: edu")

    def testSub(self):
        b = None
        b = self.engine.compile('[0-9]{4}')
        self.assertEqual(b.sub('time', 'the year of 1956 and 1957'), 'the year of time and time')

    def testSubn(self):
        b = None
        b = self.engine.compile('[0-9]{4}')
        self.assertEqual(b.subn('time', 'the year of 1956 and 1957'), ('the year of time and time', 2))

    def testFindIter(self):
        b = None
        b = self.engine.compile('[0-9]{4}')
        iter = b.finditer('the year of 1956 and 1957 and 1988', 1)
        li = [s for s in iter]
        self.assertEqual(len(li), 3)
        self.assertEqual(li[0], "1956")
        self.assertEqual(li[1], "1957")
        self.assertEqual(li[2], "1988")

    def testFullMatch(self):
        b = None
        try:
            pkgname = self.engine.load(b'package year; d = [0-9]')
            b = self.engine.compile(b'year.d{4}')
            self.assertTrue(b.valid())
        except:
            self.fail()

        m = b.fullmatch(b"1998", 1)
        self.assertTrue(m)
        self.assertEqual(m.group(), "1998")

        m = b.fullmatch(b"1998 Year", 1)
        self.assertTrue(m == None)

        m = b.fullmatch(b"1998 Year", 1, 5)
        self.assertTrue(m)
        self.assertEqual(m.group(), "1998")
        

    def testMatch(self):
        b = None
        try:
            b = self.engine.compile(b"[:digit:]+")
            self.assertTrue(b.valid())
        except:
            self.fail()

        # test short match
        try:
            m = b.match(b"321", 2)
            self.assertTrue(m)
            self.assertTrue(m.start() == 2)     # match started at char 2
            self.assertTrue(m.end() == 4)
            self.assertTrue(m.group() == "21")
            self.assertTrue(m.abend() == False)
        except:
            self.fail()

        # test no match
        try:
            m = b.match(b"xyz", 1)
            self.assertTrue(m == None)
        except:
            self.fail()

        # test long match
        inp = b"889900112233445566778899100101102103104105106107108109110xyz"
        linp = len(inp)

        try:
            m = b.match(inp, 1)
            self.assertTrue(m)
            self.assertTrue(m.start() == 1)
            self.assertTrue(m.end() == linp-3+1) # due to the "xyz" at the end
            self.assertTrue(m.group() == str23(inp[0:-3]))
            self.assertTrue(m.abend() == False)
        except:
            self.fail()

        try:
            m = b.match(inp, 10)
            self.assertTrue(m)
            self.assertTrue(m.start() == 10)
            self.assertTrue(m.end() == linp-3+1) # due to the "xyz" at the end
            self.assertTrue(m.group() == str23(inp[9:-3]))
            self.assertTrue(m.abend() == False)
        except:
            self.fail()

        #test other encoders
        try:
            m = b.match(inp, 1, encoder=b"line")
            self.assertTrue(m['match'])
            self.assertTrue(m['abend'] == False)
        except:
            self.fail()

        try:
            m = b.match(inp, 1, encoder=b"bool")
            self.assertTrue(m['match'])
            self.assertTrue(m['abend'] == False)
        except:
            self.fail()

        try:
            m = b.match(inp, 1, encoder=b"color")
            self.assertTrue(m)
            # only checking the first two chars, looking for the start of
            # ANSI color sequence
            self.assertTrue(str23(m['match'])[0] == '\x1B')
            self.assertTrue(str23(m['match'])[1] == '[')
            self.assertTrue(m['abend'] == False)
        except:
            self.fail()

    def testTrace(self):
        pkgname = self.engine.import_package(b'net')
        self.assertTrue(pkgname)
        self.net_any = self.engine.compile(b'net.any')
        self.assertTrue(self.net_any)

        dict = self.net_any.trace(b"a.b.c", 1, encoder=b"condensed")
        self.assertTrue(dict['matched'] == True)
        self.assertTrue(dict['trace'])
        self.assertTrue(len(dict['trace']) > 0)

        net_ip = self.engine.compile(b"net.ip")
        self.assertTrue(net_ip)
        dict = net_ip.trace(b"a.b.c", 1, encoder=b"condensed")
        self.assertTrue(dict['matched'] == False)
        self.assertTrue(dict['trace'])
        self.assertTrue(len(dict['trace']) > 0)

        dict = self.net_any.trace(b"a.b.c", 1, encoder=b"full")
        self.assertTrue(dict['matched'] == True)
        self.assertTrue(dict['trace'])
        self.assertTrue(len(dict['trace']) > 0)
        self.assertTrue(dict['trace'].find(b'Matched 5 chars') != -1)

        try:
            dict = self.net_any.trace(b"a.b.c", 1, encoder=b"no_such_trace_style")
            self.assertTrue(False)
        except ValueError as e:
            self.assertTrue(repr(e).find('invalid trace style') != -1)

        trace_object = self.net_any.trace(b"a.b.c", 1)
        self.assertTrue(trace_object.trace_value())
        self.assertTrue(len(trace_object.trace_value()) > 0)
        self.assertTrue('match' in trace_object.trace_value())
        self.assertTrue(trace_object.trace_value()['match'])
        self.assertTrue('nextpos' in trace_object.trace_value())
        self.assertTrue(trace_object.trace_value()['nextpos'] == 6)

    def testSearch(self):
        b = None
        try:
            pkgname = self.engine.load(b'package year; d = [0-9]')
            b = self.engine.compile('year.d{4}')
            self.assertTrue(b.valid())
        except:
            self.fail()

        m = b.search("info 1998 23 2006 time 1876", 1)
        self.assertEqual(m.group(), "1998")

    def testFindall(self):
        b = None
        try:
            pkgname = self.engine.load(b'package year; d = [0-9]')
            b = self.engine.compile('year.d{4}')
            self.assertTrue(b.valid())
        except:
            self.fail()

        matches = b.findall("info 1998 23 2006 time 1876", 1)
        self.assertTrue("1998" in matches)
        self.assertTrue("2006" in matches)
        self.assertTrue("1876" in matches)
        self.assertTrue("23" not in matches)



# -----------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Error: missing command-line parameter specifying 'local' or 'system' test")
    if sys.argv[1]=='local':
        librosiedir = '//../binaries'
        print("Loading librosie from ", librosiedir[2:])
        testdir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '../../test')
    elif sys.argv[1]=='system':
        librosiedir = rosie.librosie_system()
        print("Loading librosie from system library path")
        testdir = None
    else:
        sys.exit("Error: invalid command-line parameter (must be 'local' or 'system')")
    print("Running tests using " + sys.argv[1] + " rosie installation")
    del sys.argv[1:]
    unittest.main()
    
