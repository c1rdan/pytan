#!/usr/bin/env python
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4
# Please do not change the two lines above. See PEP 8, PEP 263.
'''Build the bin/ and winbin/ scripts'''
__author__ = 'Jim Olsen (jim.olsen@tanium.com)'
__version__ = '2.1.4'

import sys
sys.dont_write_bytecode = True
import os

my_file = os.path.abspath(sys.argv[0])
my_dir = os.path.dirname(my_file)
parent_dir = os.path.dirname(my_dir)
pytan_lib_dir = os.path.join(parent_dir, 'lib')
build_lib_dir = os.path.join(my_dir, 'lib')
path_adds = [build_lib_dir, pytan_lib_dir]

[sys.path.append(aa) for aa in path_adds if aa not in sys.path]

import pytan
import pytan.binsupport
import buildsupport
import script_definitions

if __name__ == "__main__":
    pytan.binsupport.version_check(reqver=__version__)

    output_bin = os.path.join(parent_dir, 'bin')
    output_winbin = os.path.join(parent_dir, 'winbin')

    buildsupport.clean_up(output_bin, '*.py')
    buildsupport.clean_up(output_winbin, '*.bat')

    for script_name, script_def in script_definitions.scripts.items():
        script_def.update(script_definitions.general_subs)
        script_def.update(script_definitions.script_templates)
        buildsupport.create_script(
            d=script_def,
            template_key='py_template',
            output_dir=output_bin,
            filename_template=script_definitions.py_file,
        )
        buildsupport.create_script(
            d=script_def,
            template_key='bat_template',
            output_dir=output_winbin,
            filename_template=script_definitions.bat_file,
        )
