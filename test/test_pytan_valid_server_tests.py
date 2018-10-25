#!/usr/bin/env python -ttB
"""
This contains valid functional tests for pytan.

These functional tests require a connection to a Tanium server in order to run.
The connection info is pulled from the SERVER_INFO dictionary in test/API_INFO.py.

These tests all use :mod:`ddt`, a package that provides for data driven tests via JSON files.
"""
from __future__ import print_function
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from builtins import str
import sys

# disable python from creating .pyc files everywhere
sys.dont_write_bytecode = True

import os
import glob
import unittest
import json  # noqa
import csv
import io
import tempfile

my_file = os.path.abspath(sys.argv[0])
my_dir = os.path.dirname(my_file)
root_dir = os.path.join(my_dir, os.pardir)
root_dir = os.path.abspath(root_dir)
lib_dir = os.path.join(root_dir, 'lib')
path_adds = [my_dir, lib_dir]
[sys.path.insert(0, aa) for aa in path_adds if aa not in sys.path]

import pytan
import taniumpy
from . import ddt

# get our server connection info
from .API_INFO import SERVER_INFO

# where the output files from the tests will be stored
TEST_OUT = os.path.join(tempfile.gettempdir(), 'TEST_OUT')


def chew_csv(c):
    i = io.StringIO(c)
    r = csv.reader(i)
    l = list(r)
    return l


def spew(m, l=3):
    if SERVER_INFO["testlevel"] >= l:
        print(m, file=sys.stdout)


@ddt.ddt
class ValidServerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls): # noqa
        cls.handler = pytan.Handler(**SERVER_INFO)
        m = "{}\n{}: PyTan v'{}' against Tanium v'{}' -- Valid Tests Starting\n".format
        spew(m(
            '*' * 100,
            pytan.utils.seconds_from_now(),
            pytan.__version__,
            cls.handler.session.get_server_version(),
        ), 2)

        if not hasattr(cls, 'base_type_objs'):
            # fetch objects for export tests
            kwargs = {
                'name': [
                    "Computer Name", "IP Route Details", "IP Address",
                    'Folder Contents',
                ],
                'objtype': 'sensor',
            }
            spew("TESTSETUP: Getting sensor objects for export tests of BaseType")
            cls.base_type_objs = cls.handler.get(**kwargs)

        if not hasattr(cls, 'wlus'):
            # create whitelisted_urls for getobject tests
            cls.wlus = ['test1', 'test2', 'test3']
            spew("TESTSETUP: Creating whitelisted URLs for get object tests")
            for wlu in cls.wlus:
                try:
                    cls.handler.create_whitelisted_url(url=wlu)
                except:
                    pass

        if not hasattr(cls, 'result_set_objs'):
            # ask questions for export tests
            kwargs = {
                'qtype': 'manual',
                'sensors': [
                    "Computer Name", "IP Route Details", "IP Address",
                    'Folder Contents{folderPath=C:\\Program Files}',
                ],
            }
            spew("TESTSETUP: Asking a question for export tests of ResultSet")
            cls.result_set_objs = cls.handler.ask(**kwargs)

        spew('\n' + str(cls.handler))

    @classmethod
    def tearDownClass(cls): # noqa
        m = "{}\n{}: PyTan v'{}' against Tanium v'{}' -- Valid Tests Finished".format
        spew(m(
            '*' * 100,
            pytan.utils.seconds_from_now(),
            pytan.__version__,
            cls.handler.session.get_server_version(),
        ), 2)

    def setup_test(self):
        spew("")
        return self.handler

    @ddt.file_data('ddt/ddt_valid_export_resultset.json')
    def test_valid_export_resultset(self, value):
        handler = self.setup_test()

        self.assertTrue(self.result_set_objs)
        self.assertIsInstance(self.result_set_objs['question_object'], taniumpy.Question)
        self.assertIsInstance(self.result_set_objs['question_results'], taniumpy.ResultSet)
        self.assertGreaterEqual(len(self.result_set_objs['question_results'].rows), 1)
        self.assertGreaterEqual(len(self.result_set_objs['question_results'].columns), 1)

        kwargs = {'obj': self.result_set_objs['question_results']}
        kwargs.update(value['args'])

        tests = value['tests']

        s = (
            "+++ TESTING EXPECTED EXPORT OBJECT ResultSet SUCCESS Handler.{}() with kwargs {}"
        ).format
        spew(s('export_obj', kwargs))

        export_str = handler.export_obj(**kwargs)

        self.assertTrue(export_str)
        self.assertIsInstance(export_str, (str, str))
        export_str_list = chew_csv(export_str)
        spew(export_str_list[0])
        for x in tests:
            spew("+++ EVAL TEST: %s" % x)
            try:
                self.assertTrue(eval(x))
            except Exception:
                spew("!!! EVAL TEST FAILED: '%s' - Against export string list:\n%s" % (x, export_str_list))
                raise

    @ddt.file_data('ddt/ddt_valid_export_basetype.json')
    def test_valid_export_basetype(self, value):
        handler = self.setup_test()

        self.assertTrue(self.base_type_objs)
        self.assertIsInstance(self.base_type_objs, taniumpy.BaseType)
        self.assertEquals(len(self.base_type_objs), 4)

        kwargs = {'obj': self.base_type_objs}
        kwargs.update(value['args'])

        tests = value['tests']

        s = (
            "+++ TESTING EXPECTED EXPORT OBJECT BaseType SUCCESS Handler.{}() with kwargs {}"
        ).format
        spew(s('export_obj', kwargs))

        export_str = handler.export_obj(**kwargs)

        self.assertTrue(export_str)
        self.assertIsInstance(export_str, (str, str))
        for x in tests:
            spew("+++ EVAL TEST: %s" % x)
            self.assertTrue(eval(x))

    @ddt.file_data('ddt/ddt_valid_deploy_action.json')
    def test_valid_deploy_action(self, value):
        handler = self.setup_test()

        method = value['method']
        args = value['args']

        s = "+++ TESTING EXPECTED DEPLOY ACTION SUCCESS Handler.{}() with kwargs {}".format
        spew(s(method, args))

        ret = getattr(handler, method)(**args)
        self.assertIsInstance(ret['action_object'], taniumpy.Action)
        self.assertIsInstance(ret['saved_action_object'], (taniumpy.SavedAction, type(None)))
        self.assertIsInstance(ret['package_object'], taniumpy.PackageSpec)
        self.assertIsInstance(ret['group_object'], (taniumpy.Group, type(None)))
        self.assertIsInstance(ret['action_info'], taniumpy.object_types.result_info.ResultInfo)
        self.assertIsInstance(ret['poller_object'], pytan.pollers.ActionPoller)

        get_results = args.get('get_results', True)
        if get_results:
            self.assertIsInstance(ret['action_results'], taniumpy.object_types.result_set.ResultSet)
            self.assertGreaterEqual(len(ret['action_results'].rows), 1)
            self.assertGreaterEqual(len(ret['action_results'].columns), 1)
            self.assertTrue(ret['action_result_map'])
            self.assertIsNotNone(ret['poller_success'])
            for ft in list(pytan.constants.EXPORT_MAPS['ResultSet'].keys()):
                report_file, result = handler.export_to_report_file(
                    obj=ret['action_results'],
                    export_format=ft,
                    report_dir=TEST_OUT,
                    prefix=sys._getframe().f_code.co_name + '_',
                )
                self.assertTrue(report_file)
                self.assertTrue(result)
                self.assertTrue(os.path.isfile(report_file))
                self.assertGreaterEqual(len(result), 10)

    @ddt.file_data('ddt/ddt_valid_create_object.json')
    def test_valid_create_object(self, value):
        handler = self.setup_test()
        os.chdir(my_dir)

        method = value['method']
        args = value['args']
        t_obj = eval(value['taniumpyobj'])
        delete_args = {str(k): str(v) for k, v in value['delete'].items()}

        s = (
            "+++ TESTING EXPECTED CREATE OBJECT SUCCESS Handler.{}() with kwargs {}"
        ).format
        spew(s(method, args))

        try:
            handler.delete(**delete_args)
        except Exception as e:
            spew(e)

        ret = getattr(handler, method)(**args)
        self.assertIsInstance(ret, t_obj)

        delete_obj = handler.delete(**delete_args)
        for x in delete_obj:
            self.assertIsInstance(x, t_obj)

    @ddt.file_data('ddt/ddt_valid_create_object_from_json.json')
    def test_valid_create_object_from_json(self, value):
        handler = self.setup_test()

        orig_objs = handler.get(**value['get'])

        if value['transform_attr']:
            for x in orig_objs:
                transform_val = getattr(x, value['transform_attr'])
                transform_val += value['transform_value']
                setattr(x, value['transform_attr'], transform_val)
                del_kwargs = {}
                del_kwargs['objtype'] = value['objtype']
                del_kwargs[value['transform_attr']] = transform_val
                if value['delete_before']:
                    try:
                        handler.delete(**del_kwargs)
                    except Exception as e:
                        spew(e)

        json_file, results = handler.export_to_report_file(
            obj=orig_objs,
            export_format='json',
            report_dir=TEST_OUT,
            prefix=sys._getframe().f_code.co_name + '_',
        )

        kwargs = {'objtype': value['objtype'], 'json_file': json_file}

        s = (
            "+++ TESTING EXPECTED CREATE OBJECT FROM JSON SUCCESS Handler.{}() with kwargs {}"
        ).format

        spew(s('create_from_json', kwargs))

        new_obj = handler.create_from_json(**kwargs)

        self.assertIsInstance(new_obj, eval(value['listobj']))
        for x in new_obj:
            self.assertIsInstance(x, eval(value['singleobj']))

    @ddt.file_data('ddt/ddt_valid_questions.json')
    def test_valid_question(self, value):
        handler = self.setup_test()

        method = value['method']
        args = value['args']

        parsed_q = 'parsed' in args.get('qtype', '')
        is6_5 = handler.session.platform_is_6_5()
        if not is6_5 and parsed_q:
            exc = eval('pytan.exceptions.UnsupportedVersionError')
            e = '.*not supported in version.*'
            s = (
                "+++ TESTING EXPECTED QUESTION FAILURE Handler.{}() with kwargs {}"
            ).format
            spew(s(method, args))

            with self.assertRaisesRegexp(exc, e):
                getattr(handler, method)(**args)
        else:
            s = (
                "+++ TESTING EXPECTED QUESTION SUCCESS Handler.{}() with kwargs {}"
            ).format
            spew(s(method, args))

            ret = getattr(handler, method)(**args)
            self.assertIsInstance(ret['question_object'], taniumpy.Question)
            self.assertIsInstance(ret['poller_object'], pytan.pollers.QuestionPoller)

            parsed_q = args['qtype'] == 'parsed'
            if parsed_q:
                self.assertIsInstance(ret['parse_results'], taniumpy.ParseResultGroupList)

            get_results = args.get('get_results', True)
            if get_results:
                self.assertIsNotNone(ret['poller_success'])
                self.assertIsInstance(ret['question_results'], taniumpy.ResultSet)
                self.assertGreaterEqual(len(ret['question_results'].rows), 1)
                self.assertGreaterEqual(len(ret['question_results'].columns), 1)
                for ft in list(pytan.constants.EXPORT_MAPS['ResultSet'].keys()):
                    report_file, result = handler.export_to_report_file(
                        obj=ret['question_results'],
                        export_format=ft,
                        report_dir=TEST_OUT,
                        prefix=sys._getframe().f_code.co_name + '_',
                    )
                    self.assertTrue(report_file)
                    self.assertTrue(result)
                    self.assertTrue(os.path.isfile(report_file))
                    self.assertGreaterEqual(len(result), 10)

    @ddt.file_data('ddt/ddt_valid_saved_questions.json')
    def test_valid_saved_question(self, value):
        handler = self.setup_test()

        method = value['method']
        args = value['args']

        s = (
            "+++ TESTING EXPECTED SAVED QUESTION SUCCESS Handler.{}() with kwargs {}"
        ).format
        spew(s(method, args))

        ret = getattr(handler, method)(**args)
        self.assertIsInstance(ret['saved_question_object'], taniumpy.SavedQuestion)
        self.assertIsInstance(ret['question_object'], taniumpy.Question)
        self.assertIsInstance(ret['poller_object'], (pytan.pollers.QuestionPoller, type(None)))
        self.assertIsInstance(ret['poller_success'], (type(None), type(True)))
        self.assertIsInstance(ret['question_results'], taniumpy.ResultSet)
        self.assertGreaterEqual(len(ret['question_results'].rows), 1)
        self.assertGreaterEqual(len(ret['question_results'].columns), 1)
        for ft in list(pytan.constants.EXPORT_MAPS['ResultSet'].keys()):
            report_file, result = handler.export_to_report_file(
                obj=ret['question_results'],
                export_format=ft,
                report_dir=TEST_OUT,
                prefix=sys._getframe().f_code.co_name + '_',
            )
            self.assertTrue(report_file)
            self.assertTrue(result)
            self.assertTrue(os.path.isfile(report_file))
            self.assertGreaterEqual(len(result), 10)

    @ddt.file_data('ddt/ddt_valid_get_object.json')
    def test_valid_get_object(self, value):
        handler = self.setup_test()

        method = value['method']
        args = value['args']
        tests = value['tests']

        s = (
            "+++ TESTING EXPECTED GET SUCCESS Handler.{}() with kwargs {}"
        ).format
        spew(s(method, args))

        response = getattr(handler, method)(**args)

        self.assertTrue(response)
        self.assertIsInstance(response, taniumpy.BaseType)
        for x in tests:
            spew("+++ EVAL TEST: %s" % x)
            self.assertTrue(eval(x))

        for ft in list(pytan.constants.EXPORT_MAPS['BaseType'].keys()):
            report_file, result = handler.export_to_report_file(
                obj=response, export_format=ft, report_dir=TEST_OUT,
                prefix=sys._getframe().f_code.co_name + '_',
            )
            self.assertTrue(report_file)
            self.assertTrue(result)
            self.assertTrue(os.path.isfile(report_file))
            self.assertGreaterEqual(len(result), 10)

    @ddt.file_data('ddt/ddt_invalid_export_basetype.json')
    def test_invalid_export_basetype(self, value):
        handler = self.setup_test()

        kwargs = {'obj': self.base_type_objs}
        kwargs.update(value['args'])
        exc = eval(value['exception'])
        e = value['error_str']

        s = (
            "+++ TESTING EXPECTED EXPORT OBJECT BaseType FAILURE Handler.{}() with kwargs {}"
        ).format
        spew(s('export_obj', kwargs))

        with self.assertRaisesRegexp(exc, e):
            handler.export_obj(**kwargs)

    @ddt.file_data('ddt/ddt_invalid_create_object_from_json.json')
    def test_invalid_create_object_from_json(self, value):
        handler = self.setup_test()

        orig_objs = handler.get(**value['get'])

        json_file, results = handler.export_to_report_file(
            obj=orig_objs,
            export_format='json',
            report_dir=TEST_OUT,
            prefix=sys._getframe().f_code.co_name + '_',
        )

        kwargs = {'objtype': value['objtype'], 'json_file': json_file}
        exc = eval(value['exception'])
        e = value['error_str']

        s = (
            "+++ TESTING EXPECTED CREATE OBJECT FROM JSON FAILURE Handler.{}() with kwargs {}"
        ).format
        spew(s('create_from_json', kwargs))

        with self.assertRaisesRegexp(exc, e):
            handler.create_from_json(**kwargs)

    @ddt.file_data('ddt/ddt_invalid_questions.json')
    def test_invalid_question(self, value):
        handler = self.setup_test()

        method = value['method']
        args = value['args']
        exc = eval(value['exception'])
        e = value['error_str']

        parsed_q = 'parsed' in args.get('qtype', '')
        is6_5 = handler.session.platform_is_6_5()
        if not is6_5 and parsed_q:
            exc = eval('pytan.exceptions.UnsupportedVersionError')
            e = '.*not supported in version.*'

        s = (
            "+++ TESTING EXPECTED QUESTION FAILURE Handler.{}() with kwargs {}"
        ).format
        spew(s(method, args))

        with self.assertRaisesRegexp(exc, e):
            getattr(handler, method)(**args)

    @ddt.file_data('ddt/ddt_invalid_get_object.json')
    def test_invalid_get_object(self, value):
        handler = self.setup_test()

        method = value['method']
        args = value['args']
        exc = eval(value['exception'])
        e = value['error_str']

        s = (
            "+++ TESTING EXPECTED GET FAILURE Handler.{}() with kwargs {}"
        ).format
        spew(s(method, args))

        with self.assertRaisesRegexp(exc, e):
            getattr(handler, method)(**args)

    @ddt.file_data('ddt/ddt_invalid_create_object.json')
    def test_invalid_create_object(self, value):
        handler = self.setup_test()

        method = value['method']
        args = value['args']
        exc = eval(value['exception'])
        e = value['error_str']

        s = (
            "+++ TESTING EXPECTED CREATE OBJECT FAILURE Handler.{}() with kwargs {}"
        ).format
        spew(s(method, args))

        with self.assertRaisesRegexp(exc, e):
            getattr(handler, method)(**args)

    @ddt.file_data('ddt/ddt_invalid_deploy_action.json')
    def test_invalid_deploy_action(self, value):
        handler = self.setup_test()

        method = value['method']
        args = value['args']
        exc = eval(value['exception'])
        e = value['error_str']
        args["report_dir"] = args.get('report_dir', tempfile.gettempdir())
        s = (
            "+++ TESTING EXPECTED DEPLOY ACTION FAILURE Handler.{}() with kwargs {}"
        ).format
        spew(s(method, args))

        with self.assertRaisesRegexp(exc, e):
            getattr(handler, method)(**args)

    @ddt.file_data('ddt/ddt_invalid_export_resultset.json')
    def test_invalid_export_resultset(self, value):
        handler = self.setup_test()

        kwargs = {'obj': self.result_set_objs['question_results']}
        kwargs.update(value['args'])
        exc = eval(value['exception'])
        e = value['error_str']

        s = (
            "+++ TESTING EXPECTED EXPORT OBJECT ResultSet FAILURE Handler.{}() with kwargs {}"
        ).format
        spew(s('export_obj', kwargs))

        with self.assertRaisesRegexp(exc, e):
            handler.export_obj(**kwargs)


if __name__ == "__main__":

    if not os.path.isdir(TEST_OUT):
        os.mkdir(TEST_OUT)

    test_files = glob.glob(TEST_OUT + '/*.*')
    if test_files:
        spew("Cleaning up %s old test files" % len(test_files))
        [os.unlink(x) for x in test_files]

    unittest.main(
        verbosity=SERVER_INFO["testlevel"],
        failfast=SERVER_INFO["FAILFAST"],
        catchbreak=SERVER_INFO["CATCHBREAK"],
        buffer=SERVER_INFO["BUFFER"],
    )
