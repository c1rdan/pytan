#!/usr/bin/env python
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4
# Please do not change the two lines above. See PEP 8, PEP 263.
'''Create an object of type: package from a JSON file'''
__author__ = 'Jim Olsen <jim.olsen@tanium.com>'
__version__ = '2.1.5'

import os
import sys
import re
sys.dont_write_bytecode = True

my_file = os.path.abspath(sys.argv[0])
my_name = os.path.splitext(os.path.basename(my_file))[0]
my_dir = os.path.dirname(my_file)
parent_dir = os.path.dirname(my_dir)
lib_dir = os.path.join(parent_dir, 'lib')
path_adds = [lib_dir]
[sys.path.append(aa) for aa in path_adds if aa not in sys.path]

import pytan
import pytan.binsupport

if __name__ == "__main__":
    pytan.binsupport.version_check(reqver=__version__)

    parser = pytan.binsupport.setup_create_json_object_argparser(obj='package', doc=__doc__)
    args = parser.parse_args()

    handler = pytan.binsupport.process_handler_args(parser=parser, args=args)
    response = pytan.binsupport.process_create_json_object_args(
        parser=parser, handler=handler, obj='package', args=args,
    )
