#!/usr/bin/env python
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4
# Please do not change the two lines above. See PEP 8, PEP 263.
'''generates all of the examples from the test/ddt JSON files'''
from __future__ import print_function
from builtins import object
__author__ = 'Jim Olsen (jim.olsen@tanium.com)'
__version__ = '2.1.4'

import os
import sys
import json
import glob
import pprint
import shutil
import tempfile

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
import API_INFO

pytan.binsupport.version_check(__version__)

api_info = API_INFO.SERVER_INFO
# # override 6.5 host
api_info['host'] = "10.0.1.240"

# # override 6.2 host
# api_info['host'] = "172.16.31.128"

handler = pytan.handler.Handler(**api_info)
platform_version = handler.get_server_version()
is6_5 = handler.session.platform_is_6_5()
print("Platform Version: {}".format(platform_version))

BASIC_PY_CODE = script_definitions.BASIC_PY_CODE.format(**api_info)


class ExampleProcesser(object):
    rst_examples = []
    py_examples = []
    soap_examples = []
    VERBOSE = False

    def __init__(self, verbose=False, tempdir=False):
        self.VERBOSE = verbose
        self.my_file = os.path.abspath(sys.argv[0])
        self.my_dir = os.path.dirname(self.my_file)
        self.parent_dir = os.path.dirname(self.my_dir)
        self.test_dir = os.path.join(self.parent_dir, 'test')
        self.ddt_dir = os.path.join(self.test_dir, 'ddt')

        if tempdir:
            doc_dir = os.path.join('/tmp/API_BUILDER', platform_version)
            staticdoc_dir = os.path.join('/tmp/API_BUILDER', platform_version)
        else:
            doc_dir = script_definitions.doc_source
            staticdoc_dir = script_definitions.staticdoc_source

        # output directory for RST files
        self.rst_out_dir = os.path.join(doc_dir, 'examples')
        # output directory for stdout/stderr files for RST file linkage
        self.rst_outputs_dir = os.path.join(doc_dir, '_static', 'pytan_outputs')
        # output directory for python example files
        self.pytan_example_out_dir = os.path.join(parent_dir, 'EXAMPLES', 'PYTAN_API')
        # output directory for RST API example files
        self.soap_example_out_dir = os.path.join(doc_dir, 'soap_examples', platform_version)
        # output directory for response/request files for RST file linkage
        self.soap_outputs_dir = os.path.join(staticdoc_dir, 'soap_outputs', platform_version)

    def clean_up_output_dirs(self):
        output_dirs = [
            self.rst_out_dir,
            self.pytan_example_out_dir,
            self.soap_example_out_dir,
            self.rst_outputs_dir,
            self.soap_outputs_dir,
        ]

        for i in output_dirs:
            if os.path.isdir(i):
                print("Deleting and re-making old output dir: {}".format(i))
                shutil.rmtree(i)
                os.makedirs(i)

    def indent_block(self, c):
        return '\n    ' + '\n    '.join(c.splitlines())

    def build_rst_title(self, name, sep='='):
        title_sep = "{}".format(sep * 90)
        title_name = buildsupport.get_name_title(name)
        ret = "\n{}\n{}\n".format(title_name, title_sep)
        return ret

    def build_rst_desc(self, desc):
        return "{}\n".format(desc)

    def build_rst_code_block(self, title, block, code_type='none'):
        i_block = self.indent_block(block)
        code_block = script_definitions.CODE_BLOCK_TEMPLATE.format
        code_block = code_block(title=title, code_type=code_type, code_block=i_block)
        return code_block

    def build_response_blocks(self, response_objects):
        out = '\n'.join(
            [script_definitions.RESPONSE_BLOCK_TEMPLATE.format(x) for x in response_objects]
        )
        return out

    def write_rst_include_file(self, name, stepname, out, ext, out_dir):
        filename = "{}_{}.{}".format(name, stepname, ext)
        filepath = os.path.join(out_dir, filename)
        if not out:
            out = 'None\n'
        buildsupport.write_file(filepath, out)
        return filename

    def build_pytan_rst_example(self, name, desc, py_code, py_stdout, py_stderr):
        inc_code = self.write_rst_include_file(
            name=name, stepname='code', out=py_code, ext='py', out_dir=self.rst_out_dir,
        )
        inc_stdout = self.write_rst_include_file(
            name=name, stepname='stdout', out=py_stdout, ext='txt', out_dir=self.rst_outputs_dir,
        )
        inc_stderr = self.write_rst_include_file(
            name=name, stepname='stderr', out=py_stderr, ext='txt', out_dir=self.rst_outputs_dir,
        )
        title = buildsupport.get_name_title(name)
        rst_out = script_definitions.EXAMPLE_RST_TEMPLATE.format(
            title=title, desc=desc,
            inc_code=inc_code, inc_stdout=inc_stdout, inc_stderr=inc_stderr,
        )
        return rst_out

    def magic_parser(self, out):
        pretty_out = None

        if not out:
            pretty_out = 'none'
            ext = 'txt'

        if not pretty_out:
            try:
                pretty_out = pytan.utils.xml_pretty(out)
                ext = 'xml'
            except:
                pass

        if not pretty_out:
            try:
                pretty_out = pytan.utils.jsonify(json.loads(out))
                ext = 'json'
            except:
                pass

        if not pretty_out:
            pretty_out = out
            ext = 'txt'

        return ext, pretty_out

    def build_soap_example(self, name, desc, response_objects):

        for idx, x in enumerate(response_objects):
            req = self.magic_parser(out=x.request.body)
            resp = self.magic_parser(out=x.text)
            req_headers = self.indent_block(pytan.utils.jsonify(dict(x.request.headers)))
            resp_headers = self.indent_block(pytan.utils.jsonify(dict(x.headers)))
            x.platform_version = platform_version
            x.number = idx + 1
            x.stepname = 'step_{}_response'.format(x.number)
            x.request.stepname = 'step_{}_request'.format(x.number)
            x.request.ext, x.request.pretty_out = req
            x.ext, x.pretty_out, = resp
            x.out_dir = self.soap_outputs_dir
            x.pretty_headers = resp_headers
            x.request.pretty_headers = req_headers
            x.inc_file = self.write_rst_include_file(
                name=name,
                stepname=x.stepname,
                out=x.pretty_out,
                ext=x.ext,
                out_dir=x.out_dir,
            )
            x.request.inc_file = self.write_rst_include_file(
                name=name,
                stepname=x.request.stepname,
                out=x.request.pretty_out,
                ext=x.request.ext,
                out_dir=x.out_dir,
            )
        title = buildsupport.get_name_title(name)
        steps = [script_definitions.SOAP_RST_STEP.format(response=x) for x in response_objects]
        steps = '\n'.join(steps)
        soap_out = script_definitions.SOAP_RST_HEAD.format(title=title, desc=desc, steps=steps)
        return soap_out

    def build_rst_filename(self, name):
        fn = name + '.rst'
        return fn

    def build_md_filename(self, name):
        fn = name + '.md'
        return fn

    def build_py_filename(self, name):
        fn = name + '.py'
        return fn

    def write_rst_file(self, name, out):
        filename = self.build_rst_filename(name)
        filepath = os.path.join(self.rst_out_dir, filename)
        buildsupport.write_file(filepath, out)

    def write_md_file(self, name, out, out_dir):
        filename = self.build_md_filename(name)
        filepath = os.path.join(out_dir, filename)
        buildsupport.write_file(filepath, out)

    def write_py_file(self, name, out, desc):
        filename = self.build_py_filename(name)
        filepath = os.path.join(self.pytan_example_out_dir, filename)
        buildsupport.write_file(filepath, out)
        os.chmod(filepath, 0o755)
        self.py_examples.append({'filename': filename, 'desc': desc})

    def write_soap_file(self, name, out):
        filename = self.build_rst_filename(name)
        filepath = os.path.join(self.soap_example_out_dir, filename)
        buildsupport.write_file(filepath, out)

    def make_py_readme(self, name='README.MD'):
        title = "PyTan API Python Examples"
        ti_temp = '  * {filename}: {desc}'.format

        tocitems = [ti_temp(**z).replace('\n', ' ') for z in self.py_examples]
        tocitems = '\n'.join(tocitems)

        out = script_definitions.README_MD_TEMPLATE.format(title=title, tocitems=tocitems)
        self.write_md_file(name, out, self.pytan_example_out_dir)

    def make_pytan_api_index(self):
        name = 'pytan_examples'
        index_title = 'PyTan API Examples'
        desc = "Each of these sections contains examples that show Example Python code for using a PyTan method, along with the standard output and standard error from running each example"
        index_tocitems = '\n   '.join(self.rst_examples)
        out = script_definitions.RST_INDEX_TEMPLATE.format(
            title=index_title, desc=desc, tocitems=index_tocitems,
        )
        self.write_rst_file(name, out)

    def make_soap_api_index(self):
        name = 'soap_examples_{}'.format(platform_version)
        index_title = 'SOAP API Examples for Platform Version {}'.format(platform_version)
        desc = "Each of these sections contains examples that show the HTTP request and response for each step in a given workflow."
        index_tocitems = '\n   '.join(self.soap_examples)
        out = script_definitions.RST_INDEX_TEMPLATE.format(
            title=index_title, desc=desc, tocitems=index_tocitems,
        )
        self.write_soap_file(name, out)

    def make_rst_example(self, name, desc, py_code, py_stdout, py_stderr):
        out = self.build_pytan_rst_example(name, desc, py_code, py_stdout, py_stderr)
        self.write_rst_file(name, out)

    def make_py_example(self, name, desc, py_code, py_stdout, py_stderr):
        out = script_definitions.EXAMPLE_PY_TEMPLATE.format(
            desc=desc, py_code=py_code, py_stdout=py_stdout, py_stderr=py_stderr,
        )
        self.write_py_file(name, out, desc)

    def make_soap_example(self, name, desc, response_objects):
        out = self.build_soap_example(name, desc, response_objects)
        self.soap_examples.append(name)
        self.write_soap_file(name, out)

    def build_args_str(self, args_name, args):
        args_template = '{}["{}"] = {}'.format
        args_str_list = [
            args_template(args_name, k, pprint.pformat(v)) for k, v in args.items()
        ]
        args_str = '\n'.join(args_str_list)
        return args_str

    def build_args_block(self, args_name, info, info_key, method):
        args_block = ''
        if info.get(info_key, ''):
            args_str = self.build_args_str(args_name, info[info_key])
            args_block = script_definitions.HANDLER_ARGS_TEMPLATE.format(
                args_name=args_name, args_str=args_str, method=method,
            )
        return args_block

    def process_ddt(self, ddt_file):
        ddt_basename = ddt_file.replace('ddt_', '').replace('.json', '')
        ddt = os.path.join(self.ddt_dir, ddt_file)
        ddt_tests = buildsupport.json_read(ddt)
        self.ddt_examples = []

        for name, info in sorted(list(ddt_tests.items()), key=lambda x: x[1]['priority']):
            only_65 = info.get('6_5_only', False)
            if only_65 and not is6_5:
                print("Skipping {} - not valid for 6.2 platform".format(name))
                continue

            if 'invalid' in name and 'deploy' in name:
                info["report_dir"] = info.get('report_dir', tempfile.gettempdir())

            get_args_block = self.build_args_block(
                'get_kwargs', info, 'get', 'handler.get() method',
            )
            delete_args_block = self.build_args_block(
                'delete_kwargs', info, 'delete', 'handler.delete() method',
            )
            args_block = self.build_args_block(
                'kwargs', info, 'args', 'handler() class',
            )

            method_template = script_definitions.METHOD_TEMPLATES.get(info['method_template'], '')
            method_block = method_template.format(**info)

            response_template = script_definitions.RESPONSE_TEMPLATES.get(
                info['response_template'], ''
            )
            response_block = response_template.format(**info)

            py_code_items = [
                BASIC_PY_CODE,
                get_args_block,
                delete_args_block,
                args_block,
                method_block,
                response_block
            ]

            py_code_items = [x for x in py_code_items if x]
            py_code = '\n'.join(py_code_items)

            ew = buildsupport.ExecWrap()
            ew_ret = ew.main(name=name, code_block=py_code, verbose=self.VERBOSE)
            py_stdout, py_stderr, response_objects = ew_ret

            self.make_rst_example(name, info['desc'], py_code, py_stdout, py_stderr)
            self.make_py_example(name, info['desc'], py_code, py_stdout, py_stderr)
            if info.get('xml_desc', ''):
                self.make_soap_example(name, info['xml_desc'], response_objects)

            ddt_example_file = self.build_rst_filename(name)
            self.ddt_examples.append(ddt_example_file)

        name_title = buildsupport.get_name_title(ddt_basename)

        pytan_title = 'PyTan API {} Examples'.format(name_title)
        pytan_desc = "All of the PyTan API examples for {}".format(name_title)
        pytan_tocitems = '\n   '.join(self.ddt_examples)
        pytan_index_out = script_definitions.RST_INDEX_TEMPLATE.format(
            title=pytan_title, desc=pytan_desc, tocitems=pytan_tocitems,
        )
        self.write_rst_file(ddt_basename, pytan_index_out)
        self.rst_examples.append(ddt_basename)

    def main(self, skip_files=[], all_json_files=None, clean=True):

        if clean:
            self.clean_up_output_dirs()

        ew = buildsupport.ExecWrap()
        ew_ret = ew.main(
            name=script_definitions.BASIC_NAME,
            code_block=BASIC_PY_CODE,
            verbose=self.VERBOSE,
        )
        py_stdout, py_stderr, response_objects = ew_ret

        self.make_rst_example(
            script_definitions.BASIC_NAME,
            script_definitions.BASIC_DESC,
            BASIC_PY_CODE,
            py_stdout,
            py_stderr,
        )
        self.make_py_example(
            script_definitions.BASIC_NAME,
            script_definitions.BASIC_DESC,
            BASIC_PY_CODE,
            py_stdout,
            py_stderr,
        )
        self.make_soap_example(
            script_definitions.SOAP_BASIC_NAME,
            script_definitions.SOAP_BASIC_DESC,
            response_objects,
        )
        self.rst_examples.append(script_definitions.BASIC_NAME)

        valid_json_files = sorted(glob.glob(self.ddt_dir + '/ddt_valid_*.*'))
        invalid_json_files = sorted(glob.glob(self.ddt_dir + '/ddt_invalid_*.*'))

        if not all_json_files:
            all_json_files = valid_json_files + invalid_json_files
            all_json_files = [os.path.basename(x) for x in all_json_files]

        if skip_files:
            all_json_files = [x for x in all_json_files if x not in skip_files]

        # all_json_files = all_json_files[0:1]
        for x in all_json_files:
            print("Now processing ddt file: {}".format(x))
            self.process_ddt(x)

        self.make_pytan_api_index()
        self.make_soap_api_index()
        self.make_py_readme()


if __name__ == '__main__':
    skip_files = ['ddt_invalid_connects.json']

    ep = ExampleProcesser(verbose=False, tempdir=False)
    ep.main(skip_files=skip_files, clean=True)
    console = pytan.binsupport.HistoryConsole()
