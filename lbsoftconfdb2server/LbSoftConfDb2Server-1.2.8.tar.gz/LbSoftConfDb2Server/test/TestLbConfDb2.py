###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file 'COPYING'.   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Test of the database connection string in the LbSoftConfDb2 main class

@author: Stefan-Gabriel Chitic
'''
import logging
import unittest
import json
import os

from LbSoftConfDb2Server.SoftConfDB import SoftConfDB, versionKey, sortVersions


class TestLbConfDb2(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(levelname)-8s: %(message)s')
        logging.getLogger().setLevel(logging.DEBUG)
        os.environ['NEO4JHOST'] = 'localhost'
        os.environ['NEO4JPORT'] = '7687'
        if 'NEO4JPWD' in os.environ.keys():
            os.environ.pop('NEO4JPWD')
        self.db = SoftConfDB()

    def tearDown(self):
        self.db.mNeoDB.delete_all()

    def test_bulk_retag(self):
        #  A_v1r1 -> B_v1r1 -> C_v1r1
        #  D_v1r1 -> B_v1r1 -> C_v1r1
        #  Initial insert
        graph = [{
            'project': 'A',
            'version': 'v1r1',
            'saveURIinPV': False,
            'createNode': True,
            'autorelease': True,
            'mPlatforms': [],
            'sourceuri': '',
            'commitID': 'aaaaaaaaaaaaa',
            'deps': [{
                'project': 'B',
                'version': 'v1r1',
                'saveURIinPV': False,
                'createNode': True,
                'autorelease': True,
                'mPlatforms': [],
                'sourceuri': '',
                'commitID': 'bbbbbbbbbbbb',
                'deps': [{
                    'project': 'C',
                    'version': 'v1r1',
                    'saveURIinPV': False,
                    'createNode': True,
                    'autorelease': True,
                    'mPlatforms': [],
                    'sourceuri': '',
                    'commitID': 'cccccccccc',
                    'deps': [],
                }],
            }],
        }]
        self.db.createBulkPV(json.dumps(graph))

        graph = [{
            'project': 'D',
            'version': 'v1r1',
            'saveURIinPV': False,
            'createNode': True,
            'autorelease': True,
            'mPlatforms': [],
            'sourceuri': '',
            'commitID': 'ddddddddddddd',
            'deps': [{
                'project': 'B',
                'version': 'v1r1',
                'saveURIinPV': False,
                'createNode': True,
                'autorelease': True,
                'mPlatforms': [],
                'sourceuri': '',
                'commitID': 'bbbbbbbbbbbb',
                'deps': [{
                    'project': 'C',
                    'version': 'v1r1',
                    'saveURIinPV': False,
                    'createNode': True,
                    'autorelease': True,
                    'mPlatforms': [],
                    'sourceuri': '',
                    'commitID': 'cccccccccc',
                    'deps': [],
                }],
            }],
        }]
        self.db.createBulkPV(json.dumps(graph))

        a = self.db.getPV('a', 'v1r1')
        b = self.db.getPV('b', 'v1r1')
        c = self.db.getPV('c', 'v1r1')
        d = self.db.getPV('d', 'v1r1')

        self.assertEqual(a.commitID, 'aaaaaaaaaaaaa')
        self.assertEqual(b.commitID, 'bbbbbbbbbbbb')
        self.assertEqual(c.commitID, 'cccccccccc')
        self.assertEqual(d.commitID, 'ddddddddddddd')

        self.assertTrue(('B', 'v1r1') in self.db.listDependencies('a', 'v1r1'))
        self.assertTrue(('B', 'v1r1') in self.db.listDependencies('d', 'v1r1'))
        self.assertTrue(('C', 'v1r1') in self.db.listDependencies('b', 'v1r1'))

        #  A_v1r1 -> B_v1r1 -> C_v1r2
        #  D_v1r1 -> B_v1r1 -> C_v1r2
        #  Retagging

        graph = [{
            'project': 'B',
            'version': 'v1r1',
            'saveURIinPV': False,
            'createNode': True,
            'autorelease': True,
            'mPlatforms': [],
            'sourceuri': '',
            'commitID': 'BBBBBBBBBBBBBBBBBB',
            'deps': [{
                    'project': 'C',
                    'version': 'v1r2',
                    'saveURIinPV': False,
                    'createNode': True,
                    'autorelease': True,
                    'mPlatforms': [],
                    'sourceuri': '',
                    'commitID': 'CCCCCCCC',
                    'deps': [],
                }]
        }]
        self.db.createBulkPV(json.dumps(graph))
        a = self.db.getPV('a', 'v1r1')
        b = self.db.getPV('b', 'v1r1')
        c = self.db.getPV('c', 'v1r2')
        d = self.db.getPV('d', 'v1r1')

        self.assertEqual(a.commitID, 'aaaaaaaaaaaaa')
        self.assertEqual(b.commitID, 'BBBBBBBBBBBBBBBBBB')
        self.assertEqual(c.commitID, 'CCCCCCCC')
        self.assertEqual(d.commitID, 'ddddddddddddd')

        self.assertTrue(('B', 'v1r1') in self.db.listDependencies('a', 'v1r1'))
        self.assertTrue(('B', 'v1r1') in self.db.listDependencies('d', 'v1r1'))
        self.assertTrue(('C', 'v1r2') in self.db.listDependencies('b', 'v1r1'))


    def test_version_key(self):
        self.assertEqual(versionKey('1.2.3'), (1, '.', 2, '.', 3))
        self.assertEqual(versionKey('v10r0'), ('v', 10, 'r', 0))
        self.assertEqual(versionKey('1.2-a'), (1, '.', 2, '-a') )

    def test_sortVersions(self):
        self.assertEqual(sortVersions(['v2r0', 'v1r0', 'v1r1']),
                         ['v1r0', 'v1r1', 'v2r0'])

    def test_getOrCreateProjectNode(self):
        res = self.db.createProjectNode('My_First_project',
                                         sourceuri='gitlab:myfirstproject')
        self.assertEqual(res.name, 'MY_FIRST_PROJECT')
        self.assertEqual(res.sourceuri, 'gitlab:myfirstproject')
        self.assertEqual(len(self.db.listProjects()), 1)
        # Add the same node to check if the merge is ok
        try:
            res = self.db.createProjectNode('My_First_project',
                                            sourceuri='gitlab:myfirstproject')
            self.fail("Should raise an exception")
        except:
            pass

        # Add a seconde node
        res = self.db.createProjectNode('My_Second_project',
                                        sourceuri='gitlab:mysecondprj')
        self.assertEqual(len(self.db.listProjects()), 2)
        res = self.db.listProjects()
        self.assertEqual(sorted(['MY_FIRST_PROJECT', 'MY_SECOND_PROJECT']),
                         sorted(res))
        res = self.db.listProjects(with_extra=True)
        self.assertEqual(sorted([
            ('MY_FIRST_PROJECT', 'gitlab:myfirstproject'),
            ('MY_SECOND_PROJECT', 'gitlab:mysecondprj')]), sorted(res))

    def test_getProjectNode(self):
        self.db.createProjectNode('My_First_project',
                                  sourceuri='gitlab:myfirstproject')
        res = self.db.getProjectNode('MY_FIRST_PROJECT')
        self.assertEqual(res.name, 'MY_FIRST_PROJECT')
        self.assertEqual(res.sourceuri, 'gitlab:myfirstproject')

    def test_getOrCreatePV(self):
        self.db.createPV('a', 'v1r0')
        self.db.createPV('a', 'v1r1')
        self.db.createPV('b', 'v1r0')
        self.db.createPV('c', 'v1r0')
        # Check if number of project in total
        self.assertEqual(len(self.db.listProjects()), 3)
        res = self.db.listVersions('A')
        self.assertEqual(sorted([('A', 'v1r0'), ('A', 'v1r1')]), sorted(res))
        res = self.db.listVersions('B')
        self.assertEqual([('B', 'v1r0')], res)
        res = self.db.listVersions('C')
        self.assertEqual([('C', 'v1r0')], res)
        res = self.db.createPVSerializable('D', 'v1r0')
        self.assertEqual('D_v1r0', res)

    def test_getOrCreatePVPattern(self):
        d1 = self.db.createPV("DAVINCI", "v50r0")
        f1 = self.db.createPV("fifi", "v*")
        self.db.addRequires(d1, f1)
        tmp = self.db.getPV("DAVINCI", "v50r0")
        self.assertTrue(f1 in list(tmp.requiresPattern))

        t1 = self.db.createPV("toto", "v1r0")
        tp1 = self.db.createPV("toto", "v*")
        self.db.addRequires(d1, tp1)
        tmp = self.db.getPV("DAVINCI", "v50r0")
        self.assertTrue(t1 in list(tmp.requires))

        t2 = self.db.createPV("toto", "v2r0")
        tmp = self.db.getPV("DAVINCI", "v50r0")
        self.assertTrue(t2 in list(tmp.requires))
        self.assertTrue(t1 not in list(tmp.requires))

        d2 = self.db.createPV("DAVINCI", "v50r4")
        tp2 = self.db.createPV("toto", "v2r*")
        self.db.addRequires(d2, tp2)
        tmp = self.db.getPV("DAVINCI", "v50r0")
        self.assertTrue(t2 in list(tmp.requires))
        self.assertTrue(t1 not in list(tmp.requires))

        tmp = self.db.getPV("DAVINCI", "v50r4")
        self.assertTrue(t2 in list(tmp.requires))
        self.assertTrue(t1 not in list(tmp.requires))

        t3 = self.db.createPV("toto", "v2r1")
        tmp = self.db.getPV("DAVINCI", "v50r0")
        self.assertTrue(t3 in list(tmp.requires))
        self.assertTrue(t2 not in list(tmp.requires))
        self.assertTrue(t1 not in list(tmp.requires))

        tmp = self.db.getPV("DAVINCI", "v50r4")
        self.assertTrue(t3 in list(tmp.requires))
        self.assertTrue(t2 not in list(tmp.requires))
        self.assertTrue(t1 not in list(tmp.requires))

    def test_deletePv(self):
        self.db.createPV('a', 'v1r0')
        self.db.createPV('a', 'v1r1')
        res = self.db.listVersions('A')
        self.assertEqual(sorted([('A', 'v1r0'), ('A', 'v1r1')]), sorted(res))
        self.db.deletePV('a', 'v1r1')
        res = self.db.listVersions('A')
        self.assertEqual(sorted([('A', 'v1r0')]), sorted(res))
        self.db.deletePV('a', 'v1r1')
        res = self.db.listVersions('A')
        self.assertEqual(sorted([('A', 'v1r0')]), sorted(res))

    def test_versionIsPattern(self):
        self.assertTrue(self.db.versionIsPattern('toto*re'))
        self.assertFalse(self.db.versionIsPattern('totore'))

    def test_getPV(self):
        self.db.createPV('a', 'v1r0')
        res = self.db.getPV('a', 'v1r0')
        res2 = self.db.getPVFromString('a_v1r0')
        self.assertEqual(res, res2)
        self.assertEqual(res.name, 'A_v1r0')
        self.assertEqual(res.version, 'v1r0')
        self.assertEqual(res.project_name, 'A')
        res = self.db.findVersion('toto', 'v1r0')
        self.assertEqual(res, [])
        res = self.db.findVersion('a', 'v1r0')[0]
        self.assertEqual(res, 'A_v1r0')

    def test_addPVPlatform(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        self.db.addPVPlatform('a', 'v1r0', 'x65')
        self.assertEqual(sorted(self.db.listPlatforms('A', 'v1r0')),
                         sorted(['x64', 'x65']))
        self.assertEqual(sorted(self.db.listAllPlatforms()),
                         sorted(['x64', 'x65']))

    def test_delPVPlatform(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        self.db.addPVPlatform('a', 'v1r0', 'x65')
        self.db.delPVPlatform('a', 'v1r0', 'x65')
        self.assertEqual(sorted(self.db.listPlatforms('A', 'v1r0')),
                         sorted(['x64']))
        self.db.delPVPlatform('a', 'v1r0', 'x65')
        self.assertEqual(sorted(self.db.listPlatforms('A', 'v1r0')),
                         sorted(['x64']))
        self.db.delPVPlatform('b', 'v1r0', 'x65')
        self.assertEqual(sorted(self.db.listPlatforms('A', 'v1r0')),
                         sorted(['x64']))

    def test_requires(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        self.db.addPVPlatform('a', 'v1r0', 'x65')
        self.db.addPVPlatform('b', 'v1r0', 'x65')
        self.db.addPVPlatform('b', 'v1r0', 'x64')
        a = self.db.getPV('a', 'v1r0')
        b = self.db.getPV('b', 'v1r0')
        self.db.addRequires(a, b)
        a = self.db.getPV('a', 'v1r0')
        self.assertEqual(list(a.requires)[0].name, 'B_v1r0')

    def test_listDependencies(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        self.db.addPVPlatform('a', 'v1r0', 'x65')
        self.db.addPVPlatform('b', 'v1r0', 'x64')
        self.db.addPVPlatform('c', 'v1r0', 'x64')
        self.db.addPVPlatform('d', 'v1r0', 'x64')

        a = self.db.getPV('a', 'v1r0')
        b = self.db.getPV('b', 'v1r0')
        c = self.db.getPV('c', 'v1r0')
        d = self.db.getPV('d', 'v1r0')
        self.db.addRequires(a, b)
        self.db.addRequires(b, c)
        self.db.addRequires(c, d)
        expected = [('B', 'v1r0'), ('C', 'v1r0'), ('D', 'v1r0')]
        res = self.db.listDependencies('a', 'v1r0')
        self.assertEqual(expected, res)

    def test_listReferences(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        self.db.addPVPlatform('a', 'v1r0', 'x65')
        self.db.addPVPlatform('b', 'v1r0', 'x64')
        self.db.addPVPlatform('c', 'v1r0', 'x64')
        self.db.addPVPlatform('d', 'v1r0', 'x64')

        a = self.db.getPV('a', 'v1r0')
        b = self.db.getPV('b', 'v1r0')
        c = self.db.getPV('c', 'v1r0')
        d = self.db.getPV('d', 'v1r0')
        self.db.addRequires(a, b)
        self.db.addRequires(b, c)
        self.db.addRequires(c, d)
        expected = [('C', 'v1r0'), ('B', 'v1r0'), ('A', 'v1r0')]
        res = self.db.listReferences('d', 'v1r0')
        self.assertEqual(expected, res)

    def test_listDependencyRelations(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        self.db.addPVPlatform('a', 'v1r0', 'x65')
        self.db.addPVPlatform('b', 'v1r0', 'x64')
        self.db.addPVPlatform('c', 'v1r0', 'x64')
        self.db.addPVPlatform('d', 'v1r0', 'x64')

        a = self.db.getPV('a', 'v1r0')
        b = self.db.getPV('b', 'v1r0')
        c = self.db.getPV('c', 'v1r0')
        d = self.db.getPV('d', 'v1r0')
        self.db.addRequires(a, b)
        self.db.addRequires(b, c)
        self.db.addRequires(c, d)
        res = self.db.listDependencyRelations('a', 'v1r0')
        expected = [(('A', 'v1r0'), ('B', 'v1r0')),
                    (('B', 'v1r0'), ('C', 'v1r0')),
                    (('C', 'v1r0'), ('D', 'v1r0'))]
        self.assertEqual(sorted(expected), sorted(res))
        res = self.db.listReferencesRelations('d', 'v1r0')
        self.assertEqual(sorted(expected), sorted(res))

    def test_getDependenciesAsDot(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        self.db.addPVPlatform('a', 'v1r0', 'x65')
        self.db.addPVPlatform('b', 'v1r0', 'x64')
        self.db.addPVPlatform('c', 'v1r0', 'x64')
        self.db.addPVPlatform('d', 'v1r0', 'x64')

        a = self.db.getPV('a', 'v1r0')
        b = self.db.getPV('b', 'v1r0')
        c = self.db.getPV('c', 'v1r0')
        d = self.db.getPV('d', 'v1r0')
        self.db.addRequires(a, b)
        self.db.addRequires(b, c)
        self.db.addRequires(c, d)
        res = self.db.getDependenciesAsDot([('a', 'v1r0')])
        expected = 'digraph software_deps {\nA_v1r0 -> B_v1r0\n' \
                   'B_v1r0 -> C_v1r0\nC_v1r0 ' \
                   '-> D_v1r0\n}'

        self.assertEqual(expected, res)
        res = self.db.getReferencesAsDot([('d', 'v1r0')])
        self.assertEqual(sorted(expected), sorted(res))


    def test_show(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        self.db.addPVPlatform('b', 'v1r0', 'x64')
        self.db.addPVPlatform('c', 'v1r0', 'x64')

        a = self.db.getPV('a', 'v1r0')
        b = self.db.getPV('b', 'v1r0')
        project = self.db.getProjectNode('b')
        platform = [p for p in b.platform if p.name == 'x64']
        if len(platform):
            platform = platform[0]
        else:
            platform = None
        c = self.db.getPV('c', 'v1r0')
        self.db.addRequires(a, b)
        self.db.addRequires(b, c)

        res = self.db.showProject('b')
        expected = 'Node %s Properties\n------------------------------\n' \
                   'name                          : B\n' % \
                   project.ID
        self.assertEqual(expected, res)
        res = self.db.showProject('NO_NODE')
        self.assertEqual(None, res)
        res = self.db.show('b', 'v1r0')
        expected = 'Node %s Properties\n------------------------------\n' \
                   'name                : B_v1r0\n' \
                   'project_name        : B\nversion             : v1r0\n\n' \
                   'Node %s Labels\n------------------------------\n' \
                   'active              : False\n' \
                   'patternversion      : False\n' \
                   'torelease           : False\n' \
                   'used                : False\n\n' \
                   'Node %s relationships\n' \
                   '------------------------------\n' \
                   'PLATFORM(O)     -> (ID:%s, name:x64)\n' \
                   'REQUIRES(O)     -> (ID:%s, name:C_v1r0' \
                   ', project_name:C, version:v1r0)\n' \
                   'PROJECT(I)      <- (ID:%s, name:B)\n' % (b.ID, b.ID, b.ID,
                                                             platform.ID,
                                                             c.ID,
                                                             project.ID)
        expected = '%sREQUIRES(I)     <- (ID:%s, name:A_v1r0' \
                   ', project_name:A, version:v1r0)\n' % (expected, a.ID)
        print(expected)
        print(res)
        self.assertEqual(expected, res)

    def test_PVProperties(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        res = self.db.getPVProperties('A', 'v1r0')
        try:
            self.db.getPVProperties('A', 'v1r1')
            self.fail('Should not find the project')
        except:
            pass
        expected = {'project_name': 'A',
                    'name': 'A_v1r0',
                    'version': 'v50r1'}
        self.assertEqual(sorted(res), sorted(expected))

        try:
            self.db.setPVProperty('A', 'v1r0', 'version', 'foo')
            self.fail('Version should not be editable')
        except:
            pass
        try:
            self.db.setPVProperty('A', 'v1r1', 'version', 'foo')
            self.fail('Should not find the project')
        except:
            pass
        self.db.setPVProperty('A', 'v1r0', 'sourceuri', 'foo')
        expected['sourceuri'] = 'foo'
        res = self.db.getPVProperties('A', 'v1r0')
        self.assertEqual(sorted(res), sorted(expected))
        try:
            self.db.resetPVProperties('A', 'v1r1')
            self.fail('Should not find the project')
        except:
            pass

        self.db.resetPVProperties('A', 'v1r0')
        del expected['sourceuri']
        res = self.db.getPVProperties('A', 'v1r0')
        self.assertEqual(sorted(res), sorted(expected))

    def test_ProjectProperties(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        res = self.db.getProjectProperties('A')
        expected = {'name': 'A'}
        self.assertEqual(sorted(res), sorted(expected))
        res = self.db.getProjectProperties('B')
        self.assertEqual(res, None)

    def test_getSourceURI(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        self.db.getProjectNode('a')
        self.db.setProjectProperty('A', 'sourceuri', 'gitlab:myfirstproject')
        self.db.setPVProperty('A', 'v1r0', 'sourceuri', 'test')

        res = self.db.getSourceURI('A', 'v1r0')
        self.assertEqual(res, 'test')
        res = self.db.getSourceURI('A', 'v1r1')
        self.assertEqual(res, 'gitlab:myfirstproject#v1r1')

        self.db.createProjectNode('Davinci')
        res = self.db.getSourceURI('Davinci', 'v1r1')
        self.assertEqual(res, 'DaVinci#v1r1')

    def test_ReleaseFlag(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        res = self.db.getPV('a', 'v1r0')
        self.assertFalse(res.toRelease)

        self.db.setReleaseFlag('a', 'v1r0')
        res = self.db.getPV('a', 'v1r0')
        self.assertTrue(res.toRelease)

        res = self.db.listReleaseReqs()
        self.assertEqual([('A', 'v1r0')], res)

        self.db.unsetReleaseFlag('a', 'v1r0')
        res = self.db.getPV('a', 'v1r0')
        self.assertFalse(res.toRelease)

        self.db.unsetReleaseFlag('a', 'v1r1')
        res = self.db.listReleaseReqs()
        self.assertEqual([], res)

        self.db.addPVPlatform('a', 'v1r0', 'x64')
        self.db.addPVPlatform('b', 'v1r0', 'x64')
        a = self.db.getPV('a', 'v1r0')
        b = self.db.getPV('b', 'v1r0')
        self.db.addRequires(a, b)
        try:
            self.db.setReleaseFlag('a', 'v1r0')
            self.fail("The release of a_v1r0 should not be permited")
        except:
            pass



    def test_nodesHaveRelationship(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        self.db.addPVPlatform('b', 'v1r0', 'x64')

        a = self.db.getPV('a', 'v1r0')
        b = self.db.getPV('b', 'v1r0')
        self.db.addRequires(a, b)
        self.assertTrue(self.db.nodesHaveRelationship(a, b, 'REQUIRES'))
        self.assertFalse(self.db.nodesHaveRelationship(b, a, 'REQUIRES'))

    def test_BuildTool(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64')
        self.db.addPVPlatform('b', 'v1r0', 'x64')

        a = self.db.getPV('a', 'v1r0')
        b = self.db.getPV('b', 'v1r0')
        self.db.addRequires(a, b)

        res = self.db.getBuildTools('a', 'v1r0')
        self.assertEqual(res, [])

        self.db.setBuildTool('a', 'v1r0', 'CMAKE')
        res = self.db.getBuildTools('a', 'v1r0')
        self.assertEqual(res, ['CMAKE'])

        self.db.unsetBuildTool('a', 'v1r0')
        res = self.db.getBuildTools('a', 'v1r0')
        self.assertEqual(res, [])

        self.db.setBuildTool('a', 'v1r0', 'CMT')
        res = self.db.getBuildTools('a', 'v1r0')
        self.assertEqual(res, ['CMT'])

        self.db.unsetBuildTool('a', 'v1r0')

        self.db.setBuildTool('a', 'v1r0', None)
        res = self.db.getBuildTools('a', 'v1r0')
        self.assertEqual(res, ['CMAKE'])

        res = self.db.listCMakeBuiltProjects()
        self.assertEqual(res, [('A', 'v1r0')])
        self.db.unsetBuildTool('a', 'v1r0')

        self.db.setBuildTool('b', 'v1r0', 'CMT')
        res = self.db.listCMTBuiltProjects()
        self.assertEqual(res, [('B', 'v1r0')])
        res = self.db.getBuildTools('a', 'v1r0')
        self.assertEqual(res, ['CMT'])

    def test_ProjectProperty(self):
        pv = self.db.createProjectNode('My_First_project')
        res = self.db.getProjectProperties('My_First_project')
        self.assertTrue('name' in res.keys())
        self.assertEqual('My_First_project'.upper(), res['name'])
        try:
            self.db.setProjectProperty('My_First_project', 'name',
                                       'My_First_project41')
            self.fail('Project name should not be editable')
        except:
            self.db.resetProjectProperties('My_First_project41')
            self.db.setProjectProperty('My_First_project41', 'name',
                                       'My_First_project')

        self.db.setProjectProperty('My_First_project', 'sourceuri',
                                   'toto')
        res = self.db.getProjectProperties('My_First_project')
        self.assertEqual(2, len(res.keys()))
        self.assertEqual('toto', res['sourceuri'])

        self.db.resetProjectProperties('My_First_project')
        res = self.db.getProjectProperties('My_First_project')
        self.assertTrue('name' in res.keys())
        self.assertEqual('My_First_project'.upper(), res['name'])

        res = self.db.dumpAllProjectProperties()
        self.assertTrue('My_First_project'.upper() in res.keys())
        res = res['My_First_project'.upper()]
        self.assertTrue('name' in res.keys())
        self.assertEqual('My_First_project'.upper(), res['name'])

    def test_listStackPlatformsRequestedForRelease(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64-centos7-gcc7-opt',
                              reltype='REQUESTED_PLATFORM')
        self.db.addPVPlatform('a', 'v1r0', 'x64-centos7-gcc7-dbg')
        res = self.db.listStackPlatformsRequestedForRelease('a', 'v1r0')
        self.assertEqual(sorted(res), sorted(set(['x64-centos7-gcc7-opt'])))
        self.db.addPVPlatform('a', 'v1r0', 'x64-centos7-gcc7-do0',
                              reltype='REQUESTED_PLATFORM')
        res = self.db.listStackPlatformsRequestedForRelease('a', 'v1r0')
        self.assertEqual(sorted(res), sorted(set(['x64-centos7-gcc7-opt',
                                                  'x64-centos7-gcc7-do0'])))

    def test_listStackPlatformsRequestedForRelease2(self):
        self.db.addPVPlatform('b', 'v1r0', 'x64-centos7-gcc7-dbg')
        self.db.addPVPlatform('a', 'v1r0', 'x64-centos7-gcc7-dbg')
        a = self.db.getPV('a', 'v1r0')
        b = self.db.getPV('b', 'v1r0')
        self.db.addRequires(a, b)
        try:
            self.db.addPVPlatform('a', 'v1r0', 'x64-centos7-gcc7-opt',
                                  reltype='REQUESTED_PLATFORM')
            self.fail("The new requested platform is not a subset of the "
                      "children platforms")
        except:
            pass

    def test_listStackPlatformsToRelease(self):
        self.db.addPVPlatform('a', 'v1r0', 'x64-centos7-gcc7-opt')
        self.db.addPVPlatform('a', 'v1r0', 'x64-centos7-gcc7-dbg')
        self.db.addPVPlatform('a', 'v1r0', 'x64-centos7-gcc7-do0')
        self.db.addPVPlatform('b', 'v1r0', 'x64-centos7-gcc7-do0')
        self.db.addPVPlatform('b', 'v1r0', 'x64-centos7-gcc7-dbg')
        self.db.addPVPlatform('c', 'v1r0', 'x64-centos7-gcc7-do0')
        self.db.addPVPlatform('c', 'v1r0', 'x64-centos7-gcc7-dbg')

        a = self.db.getPV('a', 'v1r0')
        b = self.db.getPV('b', 'v1r0')
        c = self.db.getPV('c', 'v1r0')

        other = self.db.createPV('e', 'v1r0')

        self.db.addRequires(a, b)
        self.db.addRequires(a, c)

        res = self.db.listStackPlatformsToRelease('a', 'v1r0')
        self.assertEqual(sorted(res), sorted(['x64-centos7-gcc7-do0',
                                              'x64-centos7-gcc7-dbg']))

        res = self.db.listStackPlatformsToRelease('e', 'v1r0')
        self.assertEqual(res, [])

    def test_listReleaseStacks(self):
        # Test the  graph: (R = release reauested)
        #             b (v2r0)R
        #          /            \
        # a(v2r0)R                   d(v2r0)R
        #          \            /
        #             c (v2r0)R
        #
        # b (v1r1)R - d(v1r1)R
        #
        # e (v0r0)R - d(v1r1)R

        self.db.addPVPlatform('a', 'v2r0', 'x64-centos7-gcc7-opt')
        self.db.addPVPlatform('b', 'v2r0', 'x64-centos7-gcc7-opt')
        self.db.addPVPlatform('b', 'v1r1', 'x64-centos7-gcc7-opt')
        self.db.addPVPlatform('c', 'v2r0', 'x64-centos7-gcc7-opt')
        self.db.addPVPlatform('d', 'v2r0', 'x64-centos7-gcc7-opt')
        self.db.addPVPlatform('d', 'v1r1', 'x64-centos7-gcc7-opt')
        self.db.addPVPlatform('e', 'v0r0', 'x64-centos7-gcc7-opt')

        self.db.addPVPlatform('a', 'v2r0', 'x64-centos7-gcc7-dbg')
        self.db.addPVPlatform('b', 'v2r0', 'x64-centos7-gcc7-dbg')
        self.db.addPVPlatform('b', 'v1r1', 'x64-centos7-gcc7-dbg')
        self.db.addPVPlatform('c', 'v2r0', 'x64-centos7-gcc7-dbg')
        self.db.addPVPlatform('d', 'v2r0', 'x64-centos7-gcc7-dbg')
        self.db.addPVPlatform('d', 'v1r1', 'x64-centos7-gcc7-dbg')

        av2r0 = self.db.getPV('a', 'v2r0')
        bv2r0 = self.db.getPV('b', 'v2r0')
        cv2r0 = self.db.getPV('c', 'v2r0')
        dv2r0 = self.db.getPV('d', 'v2r0')

        self.db.addRequires(av2r0, bv2r0)
        self.db.addRequires(av2r0, cv2r0)
        self.db.addRequires(bv2r0, dv2r0)
        self.db.addRequires(cv2r0, dv2r0)

        bv1r1 = self.db.getPV('b', 'v1r1')
        dv1r1 = self.db.getPV('d', 'v1r1')
        self.db.addRequires(bv1r1, dv1r1)

        ev0r0 = self.db.getPV('e', 'v0r0')

        self.db.setBuildTool('d', 'v2r0', "CMT")
        self.db.addPVPlatform('a', 'v2r0', 'x64-centos7-gcc7-opt',
                              'REQUESTED_PLATFORM')

        self.db.addRequires(ev0r0, dv1r1)

        self.db.setReleaseFlag('d', 'v2r0')
        self.db.setReleaseFlag('b', 'v2r0')
        self.db.setReleaseFlag('c', 'v2r0')
        self.db.setReleaseFlag('a', 'v2r0')

        self.db.setReleaseFlag('d', 'v1r1')
        self.db.setReleaseFlag('b', 'v1r1')

        self.db.setReleaseFlag('e', 'v0r0')
        expected = sorted([
            sorted([('D', 'v1r1'), ('B', 'v1r1'), ('E', 'v0r0')]),
            sorted([('B', 'v2r0'), ('D', 'v2r0'), ('A', 'v2r0'),
                    ('C', 'v2r0')])
        ])
        res = [x['path'] for x in self.db.listReleaseStacks()]
        for val in sorted(res):
            self.assertTrue(sorted(val) in expected)
        res = [x['platforms'] for x in self.db.listReleaseStacks()]
        expected = sorted([
            sorted(['x64-centos7-gcc7-opt', 'x64-centos7-gcc7-dbg']),
            sorted(['x64-centos7-gcc7-opt']),
        ])
        for val in sorted(res):
            self.assertTrue(sorted(val) in expected)

    def test_matchAndSortVersions(self):
        versions = ['v10r0', 'v10r1', 'v10r2', 'v12r1', 'v11r0']
        res = self.db.matchAndSortVersions('v10r*', versions)
        self.assertEqual(res, ['v10r0', 'v10r1', 'v10r2'])
        res = self.db.matchAndSortVersions('v1*', versions)
        self.assertEqual(res, ['v10r0', 'v10r1', 'v10r2', 'v11r0', 'v12r1'])
        try:
            res = self.db.matchAndSortVersions('v10r', versions)
            self.fail('Should not get here')
        except:
            pass

    def test_tDatapkg(self):
        pk1 = self.db.createDatapkgVersion('a', 'tck', 'datapacket1',
                                           'v1r0')
        pk2 = self.db.createDatapkgVersion('a', 'tck', 'datapacket1',
                                           'v1r1')
        pk3 = self.db.createDatapkgVersion('a', 'tck', 'datapacket2',
                                           'v1r1')
        pk4 = self.db.createDatapkgVersion('a', None, 'datapacket3',
                                           'v1r1')
        res = self.db.listDatapkgs()
        self.assertEqual(sorted(res), sorted(['DATAPACKET1', 'DATAPACKET2',
                                              'DATAPACKET3']))

        res = self.db.listDatapkgVersions('datapacket1')
        self.assertEqual(sorted(res), sorted([('DATAPACKET1', 'v1r0'),
                                              ('DATAPACKET1', 'v1r1')]))

    def test_Application(self):
        self.db.createPV('a', 'v1r0')
        self.db.createPV('a', 'v1r1')
        self.db.createPV('b', 'v1r0')
        self.db.createPV('c', 'v1r0')
        self.assertEqual(self.db.listApplications(), [])
        self.db.setApplication('b')
        self.assertEqual(len(self.db.listApplications()), 1)
        self.db.setApplication('a')
        self.assertEqual(len(self.db.listApplications()), 2)
        self.db.unsetApplication('b')
        self.assertEqual(len(self.db.listApplications()), 1)

    def test_active(self):
        self.db.createPV('a', 'v1r0')
        a = self.db.createPV('a', 'v1r1')
        b = self.db.createPV('b', 'v1r0')
        self.db.createPV('c', 'v1r0')
        self.db.addRequires(a, b)
        self.assertEqual(self.db.listActive(), [])
        try:
            self.db.setPVActive('e', 'v1r0')
            self.fail("Should raise an error")
        except:
            pass

        self.db.setPVActive('a', 'v1r0')
        self.assertEqual(self.db.listActive(), [('A', 'v1r0')])
        self.assertEqual(self.db.listActiveReferences('b', 'v1r0'), [])
        self.db.setPVActive('a', 'v1r1')
        self.assertEqual(self.db.listActiveReferences('b', 'v1r0'),
                         [('A', 'v1r1')])
        self.db.deleteActiveLinks()
        self.assertEqual(self.db.listActive(), [])
        self.db.setPVActive('a', 'v1r0')
        self.assertEqual(self.db.listActiveApplications(), [])
        self.db.setApplication('a')
        self.assertEqual(self.db.listActiveApplications(), [("A", "v1r0")])

    def test_used(self):
        self.db.createPV('a', 'v1r0')
        self.db.createPV('a', 'v1r1')
        self.db.createPV('b', 'v1r0')
        self.db.createPV('c', 'v1r0')
        self.assertEqual(self.db.listUsed(), [])
        try:
            self.db.setPVUsed('e', 'v1r0')
            self.fail("Should raise an error")
        except:
            pass
        self.db.setPVUsed('a', 'v1r0')
        self.assertEqual(self.db.listUsed(), [('A', 'v1r0')])
        self.db.setApplication('a')
        self.db.setAllAppVersionsUsed()
        self.assertEqual(sorted(self.db.listUsed()),
                         sorted([('A', 'v1r0'), ('A', 'v1r1')]))
        self.db.deleteUsedLinks()
        self.assertEqual(self.db.listUsed(), [])

    def test_unused(self):
        self.db.createPV('a', 'v1r0')
        a = self.db.createPV('a', 'v1r1')
        b = self.db.createPV('b', 'v1r0')
        self.db.createPV('c', 'v1r0')
        self.db.addRequires(a, b)
        self.db.setPVActive('a', 'v1r0')
        self.db.setPVActive('a', 'v1r1')
        self.db.setPVActive('b', 'v1r0')
        self.db.setPVActive('c', 'v1r0')
        self.db.setPVUsed('a', 'v1r1')
        self.db.setPVUsed('a', 'v1r0')
        res = self.db.checkUnused(verbose=True)
        self.assertEqual(res, [("C", "v1r0")])

    def test_tag(self):
        self.db.createPV('a', 'v1r0')
        self.db.createPV('b', 'v1r0')
        try:
            self.db.setTag('e', 'v1r0', 'toto')
            self.fail("Should raise an error")
        except:
            pass

        self.db.setTag('a', 'v1r0', 'toto')
        self.assertEqual(self.db.listTag('toto'), [("A", "v1r0", None)])
        self.db.setTag('a', 'v1r0', 'toto')
        self.db.setTag('a', 'v1r0', 'fifi')
        self.db.setTag('b', 'v1r0', 'fifi')
        self.assertEqual(sorted(self.db.listTag('fifi')),
                         sorted([("A", "v1r0", None), ("B", "v1r0", None)]))
        try:
            self.db.unsetTag('e', 'v1r0', 'toto')
            self.fail("Should raise an error")
        except:
            pass
        self.db.unsetTag('b', 'v1r0', 'fifi')
        self.assertEqual(self.db.listTag('fifi'), [("A", "v1r0", None)])

        try:
            self.db.setPlatformTag('e', 'v1r0', 'aaa', 'toto')
            self.fail("Should raise an error")
        except:
            pass
        try:
            self.db.unsetPlatformTag('e', 'v1r0', 'aaa', 'toto')
            self.fail("Should raise an error")
        except:
            pass
        self.db.addPVPlatform('a', 'v1r0', 'x64-centos7-gcc7-dbg')
        self.db.setTag('b', 'v1r0', 'titi')
        self.db.setPlatformTag('a', 'v1r0', 'x64-centos7-gcc7-dbg', 'titi')
        self.assertEqual(sorted(self.db.listTag('titi')),
                         sorted([("A", "v1r0", 'x64-centos7-gcc7-dbg'),
                                 ("B", "v1r0", None)]))
        self.db.unsetPlatformTag('a', 'v1r0', 'x64-centos7-gcc7-dbg', 'titi')
        self.assertEqual(sorted(self.db.listTag('titi')),
                         sorted([("B", "v1r0", None)]))

    def test_getOrCreateBulkPV(self):
        self.assertEqual(None, self.db.createBulkPV(json.dumps([])))
        data = [{
            'project': 'A',
            'version': 'v1r0',
            'createNode': True,
            'saveURIinPV': True,
            'autorelease': True,
            'mPlatforms': [],
            'sourceuri': 'a',
            'deps': [{
                'project': 'B',
                'version': 'v1r0',
                'createNode': True,
                'saveURIinPV': False,
                'autorelease': True,
                'mPlatforms': [],
                'deps': [{
                    'project': 'D',
                    'version': 'v1r0',
                    'createNode': True,
                    'saveURIinPV': True,
                    'autorelease': True,
                    'mPlatforms': ['plat1'],
                    'sourceuri': 'd',
                    'deps': []
                }]
                },
                {
                    'project': 'C',
                    'version': 'v1r0',
                    'createNode': False,
                    'saveURIinPV': False,
                    'autorelease': True,
                    'mPlatforms': [],
                    'deps': []
                },

            ]
        }]
        c = self.db.createPV('c', 'v1r0')

        self.db.createBulkPV(json.dumps(data))
        a = self.db.getPV('a', 'v1r0')
        b = self.db.getPV('b', 'v1r0')
        d = self.db.getPV('d', 'v1r0')

        self.assertEqual(a.name, 'A_v1r0')
        self.assertEqual(b.name, 'B_v1r0')
        self.assertEqual(c.name, 'C_v1r0')
        self.assertEqual(d.name, 'D_v1r0')

        self.assertTrue(('B', 'v1r0') in self.db.listDependencies('a', 'v1r0'))
        self.assertTrue(('D', 'v1r0') in self.db.listDependencies('b', 'v1r0'))

if __name__ == '__main__':
    unittest.main()
