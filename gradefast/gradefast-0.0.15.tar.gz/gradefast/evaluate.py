import os
import csv
import sys
import time
import glob
import traceback
import multiprocessing as mp

from gradefast import utils
from gradefast.aggregate import Aggregate
from gradefast.result import Result, ResultGroup
from gradefast.test import GFCliTest, GFTest, TestType
from gradefast.submission import Submission, SubmissionGroup

# TODO: Can I reference a file inside unzipped zips if TestType.FILE is selected
# If so how to do that?
# file_to_test is unzipped, does it unzip the zipped if its not unzipped already?? 
class Evaluate:
    def __init__(self, submissions, test, result_path='./', clean=True, timeout=10
    ):
        # Submissions contain multiple test entry points for example main.py, result.txt, result.png 
        # Multiple tests per Submission takes care of evaluating these multiple files
        # Result from each of these tests may or may not be aggregated
        # Alternatively, there can be a single test evaluating all of these files 
        # evaluate tests on each submission
        self.submissions = submissions
        self.test = test
        self.result_path = result_path
        # len of tests should be same as marking_scheme
        self.clean = True
        self.timeout = timeout


    def pkg_setup(self, submission, test):
        full_pkg_path = self.make_pkg_full_path(submission, test)
        print(full_pkg_path)
        
        matches = glob.glob(full_pkg_path)
        if len(matches) > 0:
            full_pkg_path = matches[0]
        else:
            raise FileNotFoundError('Package directory not found')
        print(full_pkg_path)
        sys.path.append(full_pkg_path)


    def run_test(self, file_path, submission, test, conn):
        result_dict = {}
        comment = ''
        exception_tr = []
        try:
            if test.test_type == TestType.PKG:
                self.pkg_setup(submission, test)
                result_dict, comment, exception_tr = test(submission)
            elif test.test_type == TestType.FILE:
                result_dict, comment, exception_tr = test(file_path, submission)
            conn.send([result_dict, comment, exception_tr])
            conn.close()
        except Exception as e:
            exception = traceback.format_exc()
            print(exception)
            conn.send([{}, '', [exception]])
            conn.close()


    # TODO(manjrekarom): Handle unzipping of zips
    def make_pkg_full_path(self, submission, test):
        file_to_test = test.file_to_test

        parition_name = ''
        if file_to_test.startswith('zip'):
            # a proper file name will consist of <team_id>_<extension><number>
            parition_name = file_to_test.split('zip')
        elif file_to_test.startswith('unzipped'):
            parition_name = file_to_test.split('unzipped')

        unzipped_pkg_path = ''
        if len(parition_name) > 2:
            raise Exception('The file to test parameter is incorrect. It should be an \
                extension type followed by an integer')
        else:
            if parition_name[0] == '':
                if utils.is_string_number(parition_name[1]) or parition_name[1] == '':
                    unzipped_pkg_path = submission.items[file_to_test]['path']
                else:
                    raise Exception('File to test should be followed by a number if at all')
            else:
                raise Exception('File to test specified doesnt look right')
        return os.path.abspath(os.path.join(unzipped_pkg_path, test.package_path))


    def _evaluate(self, submission, test):
        '''
            Returns result_dict, comment and exceptions
        '''
        try:
            result_dict = {}
            comment = ''
            exception_tr = []

            if isinstance(test, GFCliTest):
                result_dict, comment, exception_tr = test(submission)
            elif isinstance(test, GFTest):
                ctx = mp.get_context()
                par_conn, child_conn = ctx.Pipe()
                if test.test_type == TestType.FILE:
                    if submission.items.get(test.file_to_test) != None:
                        file_path = submission.items[test.file_to_test]['path']
                    else:
                        file_path = None
                    p = ctx.Process(target=self.run_test, args=(file_path, submission, test, child_conn,))
                elif test.test_type == TestType.PKG:
                    # TODO: package_path may be a list of packages
                    p = ctx.Process(target=self.run_test, args=(None, submission, test, child_conn,))
                startime = time.time()
                p.start()
                print('Before pipes')
                if par_conn.poll(timeout=self.timeout):
                    result_dict, comment, exception_tr = par_conn.recv()
                    print('After pipes')
                p.join(timeout = self.timeout)
                endtime = time.time()
                result_dict['exec_time'] = endtime - startime
                # p.terminate()
        except Exception as e:
            # log all exceptions
            # print(traceback.format_exc())
            err_tr = traceback.format_exc()
            print(err_tr)
            return {}, '', [err_tr]

        return result_dict, comment, exception_tr

    # TODO return result group
    def __call__(self):
        # evaluate
        # on each submission in submissions run each test in tests
        task_name = ''
        theme_name = ''

        if isinstance(self.submissions, SubmissionGroup):
            task_name = self.submissions.task_name
            theme_name = self.submissions.theme_name

        result_group = ResultGroup(task_name, theme_name, {})
        exceptions = []

        for idx, submission in enumerate(self.submissions):
            # print(submission.file_list)
            # evaluate
            # if marks are not given, do no transformation of result
            
            result_dict, comment, exception = self._evaluate(submission, self.test)
            print('TEAM ID: {} {}'.format(submission.team_id, result_dict))
            
            result = Result(submission.team_id, self.test.file_to_test, result_dict, 
            pkg_path=self.test.package_path, comment=comment)
            
            result_group = Aggregate.combine(ResultGroup(task_name, theme_name, 
            {result.team_id: result}), result_group)
            
            result_group.to_json(self.result_path)
            exceptions.append(exception)

        return result_group, exceptions
