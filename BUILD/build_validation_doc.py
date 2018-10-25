#!/usr/bin/env python
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4
# Please do not change the two lines above. See PEP 8, PEP 263.
'''generates all of the examples from the test/ddt JSON files'''
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
__author__ = 'Jim Olsen (jim.olsen@tanium.com)'
__version__ = '2.1.4'

import os
import sys
import io
import unittest
import tempfile
import platform
import time

sys.dont_write_bytecode = True
my_file = os.path.abspath(sys.argv[0])
my_dir = os.path.dirname(my_file)
parent_dir = os.path.dirname(my_dir)
pytan_lib_dir = os.path.join(parent_dir, 'lib')
build_lib_dir = os.path.join(my_dir, 'lib')
test_dir = os.path.join(parent_dir, 'test')
path_adds = [build_lib_dir, pytan_lib_dir, test_dir]

[sys.path.insert(0, aa) for aa in path_adds if aa not in sys.path]

import pytan
import pytan.binsupport
import buildsupport
import script_definitions

pytan.binsupport.version_check(__version__)

import test_pytan_valid_server_tests

os_version = buildsupport.determine_os_ver()
os_version_fn = os_version.replace(' ', '_')

python_version_full = sys.version.splitlines()[0]
python_version_short = platform.python_version()
now = time.localtime()
timeformat = '%Y:%m:%d %H:%M:%S %Z'
humantime = pytan.utils.human_time(now, timeformat)

if __name__ == "__main__":
    TEST_OUT = os.path.join(tempfile.gettempdir(), 'VALIDATION_TEST_OUT')

    if not os.path.isdir(TEST_OUT):
        os.mkdir(TEST_OUT)

    api_info = test_pytan_valid_server_tests.SERVER_INFO
    # override 6.5 host
    api_info['host'] = "10.0.1.240"

    # override 6.2 host
    # api_info['host'] = "172.16.31.128"

    handler = pytan.Handler(**api_info)
    platform_version = handler.get_server_version()
    print("Determined platform version: {}".format(platform_version))
    print("Determined OS version: {}".format(os_version))
    print("Determined Python version: {}".format(python_version_full))

    buildsupport.clean_up(TEST_OUT, '*')

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_pytan_valid_server_tests)

    print("Capturing stderr and stdout and launching unittests for test_pytan_valid_server_tests")

    val_stdout = io.StringIO()
    val_stderr = io.StringIO()

    sys.stdout = val_stdout
    sys.stderr = val_stderr

    try:
        unittest.TextTestRunner(stream=val_stdout, verbosity=2).run(suite)
    except:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        val_stdout_val = val_stdout.getvalue()
        val_stderr_val = val_stderr.getvalue()
        print("Exception occurred!!")
        print("stdout:\n{}".format(val_stdout_val))
        print("stderr:\n{}".format(val_stderr_val))
        raise

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    val_stdout_val = val_stdout.getvalue()
    val_stderr_val = val_stderr.getvalue()
    # print "stdout:\n{}".format(val_stdout_val)
    # print "stderr:\n{}".format(val_stderr_val)

    if val_stderr_val:
        print(val_stderr_val)
        print("STDERR output from test!")

    dir_base = 'valid_pytan_tests'
    rst_dir = os.path.join(script_definitions.doc_source, dir_base)
    output_dir = os.path.join(script_definitions.staticdoc_source, dir_base)

    stdout_fn = 'pytan_validation_test-{}-{}-{}.log'.format(
        platform_version, os_version_fn, python_version_short,
    )

    buildsupport.write_file(os.path.join(output_dir, stdout_fn), val_stdout_val)

    rst_filename = 'pytan_validation_test-{}-{}-{}.rst'.format(
        platform_version, os_version_fn, python_version_short,
    )

    rst_out = script_definitions.VALIDATION_RST_TEMPLATE.format(
        platform_version=platform_version,
        dir_base=dir_base,
        stdout_fn=stdout_fn,
        pytan_version=pytan.__version__,
        test_date=humantime,
        os_version=os_version,
        python_version_full=python_version_full,
        python_version_short=python_version_short,
    )

    buildsupport.write_file(os.path.join(rst_dir, rst_filename), rst_out)
