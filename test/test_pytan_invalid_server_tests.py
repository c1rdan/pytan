#!/usr/bin/env python -ttB
"""
This contains invalid functional tests for pytan.

These functional tests require a connection to a Tanium server in order to run.
The connection info is pulled from the SERVER_INFO dictionary in test/API_INFO.py.

These tests all use :mod:`ddt`, a package that provides for data driven tests via JSON files.
"""
from __future__ import print_function
from __future__ import absolute_import

import sys

# disable python from creating .pyc files everywhere
sys.dont_write_bytecode = True

import os
import glob
import unittest
import copy
import json  # noqa

my_file = os.path.abspath(sys.argv[0])
my_dir = os.path.dirname(my_file)
root_dir = os.path.join(my_dir, os.pardir)
root_dir = os.path.abspath(root_dir)
lib_dir = os.path.join(root_dir, 'lib')
path_adds = [my_dir, lib_dir]

for aa in path_adds:
    if aa not in sys.path:
        sys.path.insert(0, aa)

import pytan
from . import ddt
import threaded_http

# get our server connection info
from .API_INFO import SERVER_INFO

# where the output files from the tests will be stored
TEST_OUT = os.path.join(my_dir, 'TEST_OUT')


def spew(m, l=3):
    if SERVER_INFO["testlevel"] >= l:
        print(m, file=sys.stderr)


@ddt.ddt
class InvalidServerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls): # noqa
        cls.__http = threaded_http.threaded_http(port=4433, verbosity=SERVER_INFO["testlevel"])
        m = "{}: PyTan v'{}' against Tanium v'{}' -- Invalid Tests Starting".format
        spew(m(
            pytan.utils.seconds_from_now(),
            pytan.__version__,
            'N/A',
        ), 2)

    @ddt.file_data('ddt/ddt_invalid_connects.json')
    def test_invalid_connect(self, value):

        args = value['args']
        exc = eval(value['exception'])
        e = value['error_str']

        mykwargs = copy.copy(SERVER_INFO)
        mykwargs.update(args)

        spew("")
        spew("+++ TESTING EXPECTED FAILURE Handler() with kwargs %s" % (mykwargs))
        with self.assertRaisesRegexp(exc, e):
            pytan.Handler(**mykwargs)


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
    m = "{}: PyTan v'{}' against Tanium v'{}' -- All Tests Finished".format
    spew(m(
        pytan.utils.seconds_from_now(),
        pytan.__version__,
        'N/A',
    ), 2)
