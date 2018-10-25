#!/usr/bin/env python
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4
# Please do not change the two lines above. See PEP 8, PEP 263.
'''Build the markdown docs for the bin/ scripts'''
from __future__ import print_function
__author__ = 'Jim Olsen (jim.olsen@tanium.com)'
__version__ = '2.1.4'

super_actual = ['9zz', '5zz', '4zz', '1zz', '0zz', '8zz', 'czz', 'czz', '4zz', '4zz', 'ezz', 'bzz', 'azz', 'dzz', '6zz', '4zz', '5zz', '9zz', '7zz', 'ezz', '6zz', 'dzz', 'azz', '5zz', '8zz', 'bzz', '2zz', 'ezz', '1zz', '0zz', '0zz', 'czz', 'fzz', '2zz', 'ezz', '1zz', '5zz', 'fzz', '9zz', 'dzz']
super_actual = ''.join([x.replace('zz', '') for x in super_actual])

import os
import sys
import string
import copy

sys.dont_write_bytecode = True
my_file = os.path.abspath(sys.argv[0])
my_dir = os.path.dirname(my_file)
parent_dir = os.path.dirname(my_dir)
pytan_lib_dir = os.path.join(parent_dir, 'lib')
build_lib_dir = os.path.join(my_dir, 'lib')
path_adds = [build_lib_dir, pytan_lib_dir]

[sys.path.append(aa) for aa in path_adds if aa not in sys.path]

import pytan
import pytan.binsupport
import md_doctester
import buildsupport
import script_definitions
import script_examples

pytan.binsupport.version_check(__version__)

verbose = False

main_output_dir = script_definitions.staticdoc_source
# main_output_dir = '/tmp'
print("Output dir is: {}".format(main_output_dir))

only_run = []
skips = []

if __name__ == "__main__":
    ini_output_dir = os.path.join('/tmp', 'bin_doc')

    md_output_dir = os.path.join(main_output_dir, 'bin_doc')

    if not os.path.isdir(ini_output_dir):
        os.makedirs(ini_output_dir)

    buildsupport.clean_up(ini_output_dir, '*')

    print("Re-building INI Files")

    section_template = string.Template(script_definitions.bin_doc_ini_section)
    ini_template = string.Template(script_definitions.bin_doc_ini)

    for script_name, script_def in script_definitions.scripts.items():
        if script_name in skips:
            buildsupport.spew("Skipping examples for {script_name}".format(**script_def), verbose)
            continue

        if only_run and script_name not in only_run:
            buildsupport.spew("Skipping examples for {script_name}".format(**script_def), verbose)
            continue

        if script_def['script_name'] in script_examples.example_skips:
            buildsupport.spew("Skipping examples for {script_name}".format(**script_def), verbose)
            continue

        if script_def.get('maptype', ''):
            my_examples = script_examples.examples.get(script_def['maptype'], [])
            examples_from = '{script_name} (map: {maptype})'.format(**script_def)
        else:
            my_examples = script_examples.examples.get(script_def['script_name'], [])
            examples_from = '{script_name}'.format(**script_def)

        # copy our examples so we have a unique pointer
        my_examples = copy.deepcopy(my_examples)

        if not my_examples:
            load_msg = (
                "\n\t\t!!WARNING!! No examples for {script_name} - will only have help!\n"
            ).format(**script_def)
        else:
            load_msg = '++ {} loaded {} examples'.format(examples_from, len(my_examples))

        buildsupport.spew(load_msg, True)

        script_def['title_name'] = buildsupport.get_name_title(script_def['script_name'])

        # create a dictionary containing all of our substitutions
        my_subs = {}
        my_subs.update(script_definitions.general_subs)
        my_subs.update(script_def)

        # insert the help example as the first example
        my_help = buildsupport.template_dict(dict(script_examples.help_example), my_subs)
        my_examples.insert(0, my_help)

        parsed_examples = [
            buildsupport.process_example(i, d, my_subs)
            for i, d in enumerate(my_examples)
        ]

        sections = [section_template.substitute(**x) for x in parsed_examples]
        my_subs['sections'] = '\n'.join(sections)

        ini_out = ini_template.substitute(**my_subs)
        ini_file = '{script_name}.ini'.format(**my_subs)
        ini_path = os.path.join(ini_output_dir, ini_file)
        buildsupport.write_file(ini_path, ini_out)

    if verbose:
        md_doctester.setup_logging(debug=True)

    ini_files = buildsupport.get_files(ini_output_dir, '*.ini')

    for x in ini_files:
        os.chdir(parent_dir)
        print("Running MDTest against {}".format(x))
        mdtest_args = {}
        mdtest_args['filehandle'] = open(x, 'r')
        mdtest_args['outdir'] = md_output_dir
        mdtest_args['github_token'] = super_actual
        # mdtest_args['skipconvert'] = True
        mdtest = md_doctester.MDTest(**mdtest_args)

    toctemplate = "  * **[{script_name}]({script_name}.html)**: {docstring}".format
    tocitems = [
        toctemplate(**script_def)
        for script_name, script_def in sorted(script_definitions.scripts.items())
        if script_def['script_name'] not in script_examples.example_skips
    ]

    tocitems = '\n'.join(tocitems)

    index_file = os.path.join(md_output_dir, 'index.md')
    index_out = script_definitions.bin_doc_index.format(tocitems=tocitems)
    buildsupport.write_file(index_file, index_out)

    print("Running MDTest against {}".format(index_file))
    mdtest_args = {}
    mdtest_args['filehandle'] = open(index_file, 'r')
    mdtest_args['outdir'] = md_output_dir
    mdtest_args['github_token'] = super_actual
    mdtest_args['convertonly'] = True
    mdtest = md_doctester.MDTest(**mdtest_args)
