from __future__ import absolute_import, division, print_function

import os
import shutil
import unittest
from os import listdir

from examples.knowledgebases.ssbj import clean
from kadmos.cmdows import CMDOWS
from kadmos.graph import load
from kadmos.utilities.general import pdflatex_command_found

from examples.scripts.sellar_problem import run_kadmos as run_kadmos_sellar, \
    get_loop_items as get_loop_items_sellar
from examples.scripts.ssbj import run_kadmos as run_kadmos_ssbj, \
    get_loop_items as get_loop_items_ssbj


class TestOutputFiles(unittest.TestCase):

    # General test settings
    MDAO_ARCHITECTURES = 'all'

    # Utility functions
    def cmdows_schema_check(self, cmdows_dir, case_str):
        """Check a collection of CMDOWS files in a directory against the XSD definition.

        :param cmdows_dir: path to the directory with CMDOWS files
        :type cmdows_dir: str
        :param case_str: indication of the test case being executed
        :type case_str: str
        """
        for cmdows_file in listdir(cmdows_dir):
            cmdows = CMDOWS(os.path.join(cmdows_dir, cmdows_file))
            self.assertTrue(cmdows.check_schema(),
                            msg='Schema check failed for {} CMDOWS file {}.'
                            .format(case_str, cmdows_file))

    def cmdows_uid_check(self, cmdows_dir, case_str):
        """Check the UIDs in a collection of CMDOWS files in a directory.

        :param cmdows_dir: path to the directory with CMDOWS files
        :type cmdows_dir: str
        :param case_str: indication of the test case being executed
        :type case_str: str
        """
        for cmdows_file in listdir(cmdows_dir):
            cmdows = CMDOWS(os.path.join(cmdows_dir, cmdows_file))
            self.assertTrue(cmdows.check_uids(),
                            msg='UID check failed for {} CMDOWS file {}.'
                            .format(case_str, cmdows_file))

    def cmdows_references_check(self, cmdows_dir, case_str):
        """Check the references in a collection of CMDOWS files in a directory.

        :param cmdows_dir: path to the directory with CMDOWS files
        :type cmdows_dir: str
        :param case_str: indication of the test case being executed
        :type case_str: str
        """
        for cmdows_file in listdir(cmdows_dir):
            cmdows = CMDOWS(os.path.join(cmdows_dir, cmdows_file))
            self.assertTrue(cmdows.check_references(),
                            msg='References check failed for {} CMDOWS file {}.'
                            .format(case_str, cmdows_file))

    def cmdows_checks(self, cmdows_dir, case_str):
        """Perform three CMDOWS file checks on a collection of CMDOWS files in a directory.

        :param cmdows_dir: path to the directory with CMDOWS files
        :type cmdows_dir: str
        :param case_str: indication of the test case being executed
        :type case_str: str
        """
        self.cmdows_schema_check(cmdows_dir, case_str)
        self.cmdows_uid_check(cmdows_dir, case_str)
        self.cmdows_references_check(cmdows_dir, case_str)

    def files_exist_checks(self, file_dir, case_str, ext, mdao_defs):
        """Check whether a collection of files exists based on the expected files for a test case
        and the executed MDAO architecture definitions.

        :param file_dir: path to the directory containing the files
        :type file_dir: str
        :param case_str: indication of the test case being executed
        :type case_str: str
        :param ext: file extension to be checked for
        :type ext: str
        :param mdao_defs: list of MDAO architecture definitions
        :type mdao_defs: list
        """
        dir_files = [df for df in os.listdir(file_dir) if
                     os.path.isfile(os.path.join(file_dir, df))]
        # Check RCG
        self.assertTrue('RCG.{}'.format(ext) in dir_files,
                        msg='RCG.{} is missing in output files for {} case.'.format(ext, case_str))
        # Check FPG and XDSM for each architecture
        for mdao_def in mdao_defs:
            if 'sellar' in case_str:
                self.assertTrue('FPG_{}.{}'.format(mdao_def, ext) in dir_files,
                                msg='FPG_{}.{} is missing in output files for {} case.'
                                .format(mdao_def, ext, case_str))
            elif 'ssbj' in case_str and self.MDAO_ARCHITECTURES == 'all':
                self.assertTrue('FPG_MDA.{}'.format(ext) in dir_files,
                                msg='FPG_MDA.{} is missing in output files for {} case.'
                                .format(ext, case_str))
                self.assertTrue('FPG_MDO.{}'.format(ext) in dir_files,
                                msg='FPG_MDO.{} is missing in output files for {} case.'
                                .format(ext, case_str))
            self.assertTrue('Mdao_{}.{}'.format(mdao_def, ext) in dir_files,
                            msg='Mdao_{}.{} is missing in output files for {} case.'
                            .format(mdao_def, ext, case_str))
            if ext == 'kdms':  # Check for separate process graph storage with KDMS files
                self.assertTrue('Mdao_{}_mpg.{}'.format(mdao_def, ext) in dir_files,
                                msg='Mdao_{}_mpg.{} is missing in output files for {} case.'
                                .format(mdao_def, ext, case_str))

    def cmdows_integrity_checks(self, kdms_dir, case_str):
        """ Open each KDMS file in a given directory and check its integrity with the CMDOWS
        integrity check method.

        :param kdms_dir: Directory with KDMS files to be checked
        :type kdms_dir: str
        :type case_str: str
        :param case_str: file extension to be checked for
        """
        kdms_fs = [df for df in os.listdir(kdms_dir) if os.path.isfile(os.path.join(kdms_dir, df))
                   and os.path.splitext(df)[1] == '.kdms']
        kdms_fs = [df for df in kdms_fs if not df.endswith('_mpg.kdms')]
        for kdms_file in kdms_fs:
            data_graph = load(kdms_file, file_type='kdms', source_folder=kdms_dir)
            process_graph = None
            fname, fext = os.path.splitext(kdms_file)
            if os.path.isfile(os.path.join(kdms_dir, '{}_mpg{}'.format(fname, fext))):
                process_graph = load('{}_mpg{}'.format(fname, fext), file_type='kdms',
                                     source_folder=kdms_dir)
            self.assertTrue(data_graph.check_cmdows_integrity(mpg=process_graph),
                            msg='{} does not pass CMDOWS integrity check for {} case.'
                            .format(kdms_file, case_str))


class TestSellarOutputFiles(TestOutputFiles):
    """Check all the output files for the Sellar example script. The Sellar test case can be
    executed in two ways: 'math' and 'competences', using respectively only mathematical functions
    or design competences in the CMDOWS files."""

    # General test settings
    CASES = ['math', 'competences']

    @classmethod
    def setUpClass(cls):
        """Run the KADMOS scripts once for all tests."""
        super(TestSellarOutputFiles, cls).setUpClass()
        for case in cls.CASES:
            run_kadmos_sellar(cls.MDAO_ARCHITECTURES, case)

    # Sellar math mode tests
    @unittest.skipUnless('math' in CASES, 'math not included in CASES setting')
    def test_sellar_math_cmdows(self):
        self.cmdows_checks(cmdows_dir=os.path.join('sellar_problem_math', 'CMDOWS'),
                           case_str='Sellar math')

    @unittest.skipUnless('math' in CASES, 'math not included in CASES setting')
    def test_sellar_math_xdsm(self):
        self.files_exist_checks(file_dir=os.path.join('sellar_problem_math', '(X)DSM'),
                                case_str='Sellar math',
                                ext='pdf' if pdflatex_command_found() else 'tex',
                                mdao_defs=get_loop_items_sellar(self.MDAO_ARCHITECTURES))

    @unittest.skipUnless('math' in CASES, 'math not included in CASES setting')
    def test_sellar_math_kdms(self):
        self.files_exist_checks(file_dir=os.path.join('sellar_problem_math', 'KDMS'),
                                case_str='Sellar math',
                                ext='kdms',
                                mdao_defs=get_loop_items_sellar(self.MDAO_ARCHITECTURES))

    @unittest.skipUnless('math' in CASES, 'math not included in CASES setting')
    def test_sellar_math_cmdows_integrity(self):
        self.cmdows_integrity_checks(kdms_dir=os.path.join('sellar_problem_math', 'KDMS'),
                                     case_str='Sellar math')

    # Sellar competences tests
    @unittest.skipUnless('competences' in CASES, 'competences not included in CASES setting')
    def test_sellar_competences_cmdows(self):
        self.cmdows_checks(cmdows_dir=os.path.join('sellar_problem_competences', 'CMDOWS'),
                           case_str='Sellar competences')

    @unittest.skipUnless('competences' in CASES, 'competences not included in CASES setting')
    def test_sellar_competences_xdsm(self):
        self.files_exist_checks(file_dir=os.path.join('sellar_problem_competences', '(X)DSM'),
                                case_str='Sellar competences',
                                ext='pdf' if pdflatex_command_found() else 'tex',
                                mdao_defs=get_loop_items_sellar(self.MDAO_ARCHITECTURES))

    @unittest.skipUnless('competences' in CASES, 'competences not included in CASES setting')
    def test_sellar_competences_kdms(self):
        self.files_exist_checks(file_dir=os.path.join('sellar_problem_competences', 'KDMS'),
                                case_str='Sellar competences',
                                ext='kdms',
                                mdao_defs=get_loop_items_sellar(self.MDAO_ARCHITECTURES))

    @unittest.skipUnless('competences' in CASES, 'competences not included in CASES setting')
    def test_sellar_competences_cmdows_integrity(self):
        self.cmdows_integrity_checks(kdms_dir=os.path.join('sellar_problem_competences', 'KDMS'),
                                     case_str='Sellar competences')

    # Tear-down class to clean up after tests are performed
    @classmethod
    def tearDownClass(cls):
        # Remove created directories
        super(TestSellarOutputFiles, cls).tearDownClass()
        dirs = [name for name in os.listdir('.') if os.path.isdir(name) and 'sellar' in name]
        for dr in dirs:
           shutil.rmtree(dr)


class TestSsbjOutputFiles(TestOutputFiles):

    @classmethod
    def setUpClass(cls):
        """Run the KADMOS scripts once for all tests."""
        super(TestSsbjOutputFiles, cls).setUpClass()
        run_kadmos_ssbj(cls.MDAO_ARCHITECTURES)

    def test_ssbj_cmdows(self):
        self.cmdows_checks(cmdows_dir=os.path.join('ssbj', 'CMDOWS'),
                           case_str='SSBJ')

    def test_ssbj_xdsm(self):
        self.files_exist_checks(file_dir=os.path.join('ssbj', '(X)DSM'),
                                case_str='SSBJ',
                                ext='pdf' if pdflatex_command_found() else 'tex',
                                mdao_defs=get_loop_items_ssbj(self.MDAO_ARCHITECTURES))

    def test_ssbj_kdms(self):
        self.files_exist_checks(file_dir=os.path.join('ssbj', 'KDMS'),
                                case_str='SSBJ',
                                ext='kdms',
                                mdao_defs=get_loop_items_ssbj(self.MDAO_ARCHITECTURES))

    def test_ssbj_cmdows_integrity(self):
        self.cmdows_integrity_checks(kdms_dir=os.path.join('ssbj', 'KDMS'),
                                     case_str='SSBJ')

    # Tear-down class to clean up after tests are performed
    @classmethod
    def tearDownClass(cls):
        # Remove created directories
        super(TestSsbjOutputFiles, cls).tearDownClass()
        dirs = [name for name in os.listdir('.') if os.path.isdir(name) and 'ssbj' in name]
        for dr in dirs:
           shutil.rmtree(dr)
        clean()


if __name__ == '__main__':
    unittest.main()
