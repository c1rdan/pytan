#!/usr/bin/env python -ttB
"""
This contains unit tests for pytan.

These unit tests do not require a connection to a Tanium server in order to run.
"""
from __future__ import absolute_import
import sys

# disable python from creating .pyc files everywhere
sys.dont_write_bytecode = True

import os
import unittest

my_file = os.path.abspath(sys.argv[0])
my_dir = os.path.dirname(my_file)
root_dir = os.path.join(my_dir, os.pardir)
root_dir = os.path.abspath(root_dir)
lib_dir = os.path.join(root_dir, 'lib')
path_adds = [my_dir, lib_dir]

[sys.path.append(aa) for aa in path_adds if aa not in sys.path]

import pytan
import pytan.binsupport
import taniumpy

try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET

# get our server connection info
from API_INFO import SERVER_INFO

# set logging for all logs in pytan to same level as loglevel
pytan.utils.setup_console_logging()
pytan.utils.set_log_levels(SERVER_INFO["loglevel"])


class TestDehumanizeSensorUtils(unittest.TestCase):
    def test_single_str(self):
        sensors = 'Sensor1'
        sensor_defs = pytan.utils.dehumanize_sensors(sensors)
        exp = [{'filter': {}, 'params': {}, 'options': {}, 'name': 'Sensor1'}]
        self.assertEquals(sensor_defs, exp)

    def test_single_str_with_filter(self):
        sensors = 'Sensor1, that is:.*'
        sensor_defs = pytan.utils.dehumanize_sensors(sensors)
        exp = [
            {
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*'
                },
                'params': {},
                'name': 'Sensor1',
                'options': {}
            }
        ]
        self.assertEquals(sensor_defs, exp)

    def test_single_str_complex1(self):
        sensors = (
            'Sensor1, that is:.*, opt:value_type:string, opt:ignore_case, '
            'opt:max_data_age:3600, opt:match_any_value'
        )
        sensor_defs = pytan.utils.dehumanize_sensors(sensors)
        exp = [
            {
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*'
                },
                'params': {},
                'name': 'Sensor1',
                'options': {
                    'all_values_flag': 0,
                    'ignore_case_flag': 1,
                    'max_age_seconds': '3600',
                    'value_type': 'string',
                    'all_times_flag': 0
                }
            }
        ]
        self.assertEquals(sensor_defs, exp)

    def test_single_str_complex2(self):
        sensors = (
            'Sensor1{k1=v1,k2=v2}, that is:.*, opt:value_type:string, '
            'opt:ignore_case, opt:max_data_age:3600, opt:match_any_value'
        )
        sensor_defs = pytan.utils.dehumanize_sensors(sensors)
        exp = [
            {
                'filter': {
                    'not_flag': 0,
                    'operator': 'RegexMatch',
                    'value': '.*'
                },
                'name': 'Sensor1',
                'options': {
                    'all_times_flag': 0,
                    'all_values_flag': 0,
                    'ignore_case_flag': 1,
                    'max_age_seconds': '3600',
                    'value_type': 'string'
                },
                'params': {'k1': 'v1', 'k2': 'v2'}
            }
        ]
        self.assertEquals(sensor_defs, exp)

    def test_multi_list_complex(self):
        sensors = [
            'Computer Name',
            'id:1',
            'Operating System, that contains:Windows',
            ('Sensor1{k1=v1,k2=v2}, that is:.*, opt:value_type:string, '
             'opt:ignore_case, opt:max_data_age:3600, opt:match_any_value'),
        ]
        sensor_defs = pytan.utils.dehumanize_sensors(sensors)
        exp = [
            {
                'filter': {},
                'params': {},
                'name': 'Computer Name',
                'options': {}
            },
            {
                'filter': {},
                'params': {},
                'id': '1',
                'options': {}
            },
            {
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*Windows.*'
                },
                'params': {},
                'name': 'Operating System',
                'options': {}
            },
            {
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*'
                },
                'params': {'k2': 'v2', 'k1': 'v1'},
                'name': 'Sensor1',
                'options': {
                    'all_values_flag': 0,
                    'ignore_case_flag': 1,
                    'max_age_seconds': '3600',
                    'value_type': 'string',
                    'all_times_flag': 0
                }
            }
        ]
        self.assertEquals(sensor_defs, exp)

    def test_valid_simple_str_id_selector(self):
        sensors = 'id:1'
        sensor_defs = pytan.utils.dehumanize_sensors(sensors)
        exp = [{'filter': {}, 'params': {}, 'options': {}, 'id': '1'}]
        self.assertEquals(sensor_defs, exp)

    def test_valid_simple_str_hash_selector(self):
        sensors = 'hash:1'
        sensor_defs = pytan.utils.dehumanize_sensors(sensors)
        exp = [{'filter': {}, 'params': {}, 'options': {}, 'hash': '1'}]
        self.assertEquals(sensor_defs, exp)

    def test_valid_simple_str_name_selector(self):
        sensors = 'name:Sensor1'
        sensor_defs = pytan.utils.dehumanize_sensors(sensors)
        exp = [{'filter': {}, 'params': {}, 'options': {}, 'name': 'Sensor1'}]
        self.assertEquals(sensor_defs, exp)

    def test_valid_simple_list(self):
        sensors = ['Sensor1']
        sensor_defs = pytan.utils.dehumanize_sensors(sensors)
        exp = [{'filter': {}, 'params': {}, 'options': {}, 'name': 'Sensor1'}]
        self.assertEquals(sensor_defs, exp)

    def test_empty_args_str(self):
        e = "A string or list of strings must be supplied as 'sensors'!"
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            pytan.utils.dehumanize_sensors('', empty_ok=False)

    def test_empty_args_list(self):
        e = "A string or list of strings must be supplied as 'sensors'!"
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            pytan.utils.dehumanize_sensors([], empty_ok=False)

    def test_empty_args_dict(self):
        e = "A string or list of strings must be supplied as 'sensors'!"
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            pytan.utils.dehumanize_sensors({})


class TestDehumanizeQuestionFilterUtils(unittest.TestCase):
    def test_single_filter_str(self):
        question_filters = 'Sensor1, that contains:Windows'
        question_filter_defs = pytan.utils.dehumanize_question_filters(
            question_filters
        )
        exp = [
            {
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*Windows.*'
                },
                'params': {},
                'name': 'Sensor1'
            }
        ]
        self.assertEquals(question_filter_defs, exp)

    def test_single_filter_list(self):
        question_filters = ['Sensor1, that contains:Windows']
        question_filter_defs = pytan.utils.dehumanize_question_filters(
            question_filters
        )
        exp = [
            {
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*Windows.*'
                },
                'params': {},
                'name': 'Sensor1'
            }
        ]
        self.assertEquals(question_filter_defs, exp)

    def test_multi_filter_list(self):
        question_filters = [
            'Sensor1, that contains:Windows',
            'Sensor2, that does not contain:10.10.10.10',
        ]
        question_filter_defs = pytan.utils.dehumanize_question_filters(
            question_filters
        )
        exp = [
            {
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*Windows.*'
                },
                'params': {},
                'name': 'Sensor1'
            },
            {
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 1,
                    'value': '.*10.10.10.10.*'
                },
                'params': {},
                'name': 'Sensor2'
            }
        ]
        self.assertEquals(question_filter_defs, exp)

    def test_empty_filterstr(self):
        question_filters = ''
        question_filter_defs = pytan.utils.dehumanize_question_filters(
            question_filters
        )
        exp = []
        self.assertEquals(question_filter_defs, exp)

    def test_empty_filterlist(self):
        question_filters = []
        question_filter_defs = pytan.utils.dehumanize_question_filters(
            question_filters
        )
        exp = []
        self.assertEquals(question_filter_defs, exp)

    def test_invalid_filter1(self):
        o = 'Sensor1, that feels:funny'
        e = "Filter .* is not a valid filter!"
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            pytan.utils.dehumanize_question_filters(o)

    def test_invalid_filter2(self):
        o = 'Sensor1'
        e = "Filter .* is not a valid filter!"
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            pytan.utils.dehumanize_question_filters(o)

    def test_invalid_filter3(self):
        o = 'Sensor1, th'
        e = "Filter .* is not a valid filter!"
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            pytan.utils.dehumanize_question_filters(o)


class TestDehumanizeQuestionOptionUtils(unittest.TestCase):
    def test_empty_optionstr(self):
        question_options = ''
        question_option_defs = pytan.utils.dehumanize_question_options(
            question_options
        )
        exp = {}
        self.assertEquals(question_option_defs, exp)

    def test_empty_optionlist(self):
        question_options = []
        question_option_defs = pytan.utils.dehumanize_question_options(
            question_options
        )
        exp = {}
        self.assertEquals(question_option_defs, exp)

    def test_option_str(self):
        question_options = 'ignore_case'
        question_option_defs = pytan.utils.dehumanize_question_options(
            question_options
        )
        exp = {'ignore_case_flag': 1}
        self.assertEquals(question_option_defs, exp)

    def test_option_list_single(self):
        question_options = ['ignore_case']
        question_option_defs = pytan.utils.dehumanize_question_options(
            question_options
        )
        exp = {'ignore_case_flag': 1}
        self.assertEquals(question_option_defs, exp)

    def test_option_list_multi(self):
        question_options = ['ignore_case', 'and']
        question_option_defs = pytan.utils.dehumanize_question_options(
            question_options
        )
        exp = {'ignore_case_flag': 1, 'and_flag': 1}
        self.assertEquals(question_option_defs, exp)

    def test_option_list_many(self):
        question_options = [
            'ignore_case', 'and', 'value_type:string', 'max_data_age:3600',
        ]
        question_option_defs = pytan.utils.dehumanize_question_options(
            question_options
        )
        exp = {
            'value_type': 'string',
            'ignore_case_flag': 1,
            'max_age_seconds': '3600',
            'and_flag': 1
        }
        self.assertEquals(question_option_defs, exp)

    def test_invalid_option1(self):
        o = 'willy wonka'
        e = "Option '{}' is not a valid option!".format(o)
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            question_options = [o]
            pytan.utils.dehumanize_question_options(question_options)

    def test_invalid_option2(self):
        o = 'willy wonka'
        e = "Option '{}' is not a valid option!".format(o)
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            question_options = o
            pytan.utils.dehumanize_question_options(question_options)


class TestDehumanizeExtractionUtils(unittest.TestCase):
    def test_extract_selector(self):
        s = 'id:1 more:stuff,here'
        exp = ('1 more:stuff,here', 'id')
        self.assertEquals(pytan.utils.extract_selector(s), exp)

    def test_extract_selector_use_name_if_noselector(self):
        s = 'Sensor1 more:stuff,here'
        exp = ('Sensor1 more:stuff,here', 'name')
        r = pytan.utils.extract_selector(s)
        self.assertEquals(r, exp)

    def test_extract_params(self):
        s = 'Sensor1{k1=v1,k2=v2}, more:stuff,here'
        exp = ('Sensor1, more:stuff,here', {'k2': 'v2', 'k1': 'v1'})
        r = pytan.utils.extract_params(s)
        self.assertEquals(r, exp)

    def test_extract_params_noparams(self):
        s = 'Sensor1, more:stuff,here'
        exp = ('Sensor1, more:stuff,here', {})
        r = pytan.utils.extract_params(s)
        self.assertEquals(r, exp)

    def test_extract_options_single(self):
        s = 'Sensor1, more:stuff,here, opt:ignore_case'
        exp = ('Sensor1, more:stuff,here', {'ignore_case_flag': 1})
        r = pytan.utils.extract_options(s)
        self.assertEquals(r, exp)

    def test_extract_options_many(self):
        s = (
            'Sensor1, more:stuff,here, opt:ignore_case, opt:max_data_age:3600'
            ', opt:match_any_value, opt:value_type:string'
        )
        exp = (
            'Sensor1, more:stuff,here',
            {
                'value_type': 'string',
                'ignore_case_flag': 1,
                'max_age_seconds': '3600',
                'all_values_flag': 0,
                'all_times_flag': 0
            }
        )
        r = pytan.utils.extract_options(s)
        self.assertEquals(r, exp)

    def test_extract_options_nooptions(self):
        s = 'Sensor1, more:stuff,here'
        exp = ('Sensor1, more:stuff,here', {})
        r = pytan.utils.extract_options(s)
        self.assertEquals(r, exp)

    def test_extract_filter_valid(self):
        s = 'Sensor1, that is:.*'
        exp = (
            'Sensor1',
            {'operator': 'RegexMatch', 'not_flag': 0, 'value': '.*'}
        )
        r = pytan.utils.extract_filter(s)
        self.assertEquals(r, exp)

    def test_extract_filter_valid_all(self):
        for x in pytan.constants.FILTER_MAPS:
            for y in x['human']:
                z = pytan.utils.extract_filter('Sensor1, that {}:test value'.format(y))
                self.assertTrue(z)
                self.assertEquals(len(z), 2)
                self.assertEquals(z[0], 'Sensor1')
                self.assertIn('test value', z[1]['value'])

    def test_extract_filter_nofilter(self):
        s = 'Sensor1'
        exp = ('Sensor1', {})
        r = pytan.utils.extract_filter(s)
        self.assertEquals(r, exp)

    def test_extract_params_multiparams(self):
        s = 'Sensor1{k1=v1,k2=v2}{}, more:stuff,here'
        e = "More than one parameter \(\{\}\) passed in '.*'"
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            pytan.utils.extract_params(s)

    def test_extract_params_missing_seperator(self):
        s = 'Sensor1{v1,v2}, more:stuff,here'
        e = "Parameter v1 missing key/value seperator \(=\)"
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            pytan.utils.extract_params(s)

    def test_extract_options_missing_value_max_data_age(self):
        s = 'Sensor1, more:stuff,here, opt:max_data_age'
        if sys.version_info < (3, 0):
            e = (
                "Option 'max_data_age' is missing a <type 'int'> value of seconds"
                ".*"
            )
        else:
            e = (
                "Option 'max_data_age' is missing a <class 'int'> value of seconds"
                ".*"
            )
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            pytan.utils.extract_options(s)

    def test_extract_options_missing_value_value_type(self):
        s = 'Sensor1, more:stuff,here, opt:value_type'
        if sys.version_info < (3, 0):
            e = (
                "Option 'value_type' is missing a <type 'str'> value of "
                "value_type.*"
            )
        else:
            e = (
                "Option 'value_type' is missing a <class 'str'> value of "
                "value_type.*"
            )
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            pytan.utils.extract_options(s)

    def test_extract_options_invalid_option(self):
        s = 'Sensor1, more:stuff,here, opt:invalid_option'
        e = "Option 'invalid_option' is not a valid option!"
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            pytan.utils.extract_options(s)

    def test_extract_filter_invalid(self):
        s = 'Sensor1, that meets:.*'
        e = "Filter .* is not a valid filter!"
        with self.assertRaisesRegexp(pytan.exceptions.HumanParserError, e):
            pytan.utils.extract_filter(s)


class TestManualSensorDefParseUtils(unittest.TestCase):
    def test_parse_str1(self):
        '''simple str is parsed into list of same str'''
        kwargs = {'sensor_defs': 'Sensor1'}
        r = pytan.utils.parse_defs(
            defname='sensor_defs',
            deftypes=['list()', 'str()', 'dict()'],
            strconv='name',
            empty_ok=False,
            **kwargs
        )
        exp = [{'name': 'Sensor1'}]
        self.assertEquals(r, exp)

    def test_parse_dict_name(self):
        '''dict with name is parsed into list of same dict'''
        kwargs = {'sensor_defs': {'name': 'Sensor1'}}
        r = pytan.utils.parse_defs(
            defname='sensor_defs',
            deftypes=['list()', 'str()', 'dict()'],
            strconv='name',
            empty_ok=False,
            **kwargs
        )
        exp = [{'name': 'Sensor1'}]
        self.assertEquals(r, exp)

    def test_parse_dict_id(self):
        '''dict with id is parsed into list of same dict'''
        kwargs = {'sensor_defs': {'id': '1'}}
        r = pytan.utils.parse_defs(
            defname='sensor_defs',
            deftypes=['list()', 'str()', 'dict()'],
            strconv='name',
            empty_ok=False,
            **kwargs
        )
        exp = [{'id': '1'}]
        self.assertEquals(r, exp)

    def test_parse_dict_hash(self):
        '''dict with hash is parsed into list of same dict'''
        kwargs = {'sensor_defs': {'hash': '1'}}
        r = pytan.utils.parse_defs(
            defname='sensor_defs',
            deftypes=['list()', 'str()', 'dict()'],
            strconv='name',
            empty_ok=False,
            **kwargs
        )
        exp = [{'hash': '1'}]
        self.assertEquals(r, exp)

    def test_parse_complex(self):
        '''list with many items is parsed into same list'''
        sensor_defs = [
            {
                'filter': {},
                'params': {},
                'name': 'Computer Name',
                'options': {}
            },
            {
                'filter': {},
                'params': {},
                'id': '1',
                'options': {}
            },
            {
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*Windows.*'
                },
                'params': {},
                'name': 'Operating System',
                'options': {}
            },
            {
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*'
                },
                'params': {'k2': 'v2', 'k1': 'v1'},
                'name': 'Sensor1',
                'options': {
                    'all_values_flag': 0,
                    'ignore_case_flag': 1,
                    'max_age_seconds': '3600',
                    'value_type': 'string',
                    'all_times_flag': 0
                }
            }
        ]
        kwargs = {'sensor_defs': sensor_defs}

        r = pytan.utils.parse_defs(
            defname='sensor_defs',
            deftypes=['list()', 'str()', 'dict()'],
            strconv='name',
            empty_ok=False,
            **kwargs
        )
        self.assertEquals(r, sensor_defs)

    def test_parse_noargs(self):
        '''no args throws exception'''
        kwargs = {}
        e = (
            "'sensor_defs' requires a non-empty value of type: list\(\) or "
            "str\(\) or dict\(\)"
        )
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            pytan.utils.parse_defs(
                defname='sensor_defs',
                deftypes=['list()', 'str()', 'dict()'],
                strconv='name',
                empty_ok=False,
                **kwargs
            )

    def test_parse_none(self):
        '''args==None throws exception'''
        e = (
            "'sensor_defs' requires a non-empty value of type: list\(\) or "
            "str\(\) or dict\(\)"
        )
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            kwargs = {'sensor_defs': None}
            pytan.utils.parse_defs(
                defname='sensor_defs',
                deftypes=['list()', 'str()', 'dict()'],
                strconv='name',
                empty_ok=False,
                **kwargs
            )

    def test_parse_emptystr(self):
        '''args=='' throws exception'''
        e = (
            "'sensor_defs' requires a non-empty value of type: list\(\) or "
            "str\(\) or dict\(\)"
        )
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            kwargs = {'sensor_defs': ''}
            pytan.utils.parse_defs(
                defname='sensor_defs',
                deftypes=['list()', 'str()', 'dict()'],
                strconv='name',
                empty_ok=False,
                **kwargs
            )

    def test_parse_emptylist(self):
        '''args==[] throws exception'''
        e = (
            "'sensor_defs' requires a non-empty value of type: list\(\) or "
            "str\(\) or dict\(\)"
        )
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            kwargs = {'sensor_defs': []}
            pytan.utils.parse_defs(
                defname='sensor_defs',
                deftypes=['list()', 'str()', 'dict()'],
                strconv='name',
                empty_ok=False,
                **kwargs
            )

    def test_parse_emptydict(self):
        '''args=={} throws exception'''
        e = (
            "'sensor_defs' requires a non-empty value of type: list\(\) or "
            "str\(\) or dict\(\)"
        )
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            kwargs = {'sensor_defs': {}}
            pytan.utils.parse_defs(
                defname='sensor_defs',
                deftypes=['list()', 'str()', 'dict()'],
                strconv='name',
                empty_ok=False,
                **kwargs
            )


class TestManualQuestionFilterDefParseUtils(unittest.TestCase):
    def test_parse_noargs(self):
        kwargs = {}
        r = pytan.utils.parse_defs(
            defname='question_filter_defs',
            deftypes=['list()', 'dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertFalse(r)

    def test_parse_none(self):
        kwargs = {'question_filter_defs': None}
        r = pytan.utils.parse_defs(
            defname='question_filter_defs',
            deftypes=['list()', 'dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertFalse(r)

    def test_parse_emptystr(self):
        kwargs = {'question_filter_defs': ''}
        r = pytan.utils.parse_defs(
            defname='question_filter_defs',
            deftypes=['list()', 'dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertFalse(r)

    def test_parse_emptylist(self):
        kwargs = {'question_filter_defs': []}
        r = pytan.utils.parse_defs(
            defname='question_filter_defs',
            deftypes=['list()', 'dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertFalse(r)

    def test_parse_emptydict(self):
        kwargs = {'question_filter_defs': {}}
        r = pytan.utils.parse_defs(
            defname='question_filter_defs',
            deftypes=['list()', 'dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertFalse(r)

    def test_parse_single_filter(self):
        kwargs = {'question_filter_defs': {
            'filter': {
                'operator': 'RegexMatch',
                'not_flag': 0,
                'value': '.*Windows.*'
            },
            'name': 'Operating System',
        }}
        r = pytan.utils.parse_defs(
            defname='question_filter_defs',
            deftypes=['list()', 'dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertEquals(r, [kwargs['question_filter_defs']])

    def test_parse_multi_filter(self):
        kwargs = {'question_filter_defs': [
            {
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*Windows.*'
                },
                'name': 'Operating System',
            },
            {
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 1,
                    'value': '.*Linux.*'
                },
                'name': 'Operating System',
            },
        ]}
        r = pytan.utils.parse_defs(
            defname='question_filter_defs',
            deftypes=['list()', 'dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertEquals(r, kwargs['question_filter_defs'])

    def test_parse_str(self):
        if sys.version_info < (3, 0):
            e = (
                "Argument 'question_filter_defs' has an invalid type "
                "<type 'str'>"
            )
        else:
            e = (
                "Argument 'question_filter_defs' has an invalid type "
                "<class 'str'>"
            )
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            kwargs = {'question_filter_defs': 'no string allowed'}
            pytan.utils.parse_defs(
                defname='question_filter_defs',
                deftypes=['list()', 'dict()'],
                empty_ok=True,
                **kwargs
            )


class TestManualQuestionOptionDefParseUtils(unittest.TestCase):
    def test_parse_noargs(self):
        kwargs = {}
        r = pytan.utils.parse_defs(
            defname='question_option_defs',
            deftypes=['dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertFalse(r)

    def test_parse_none(self):
        kwargs = {'question_option_defs': None}
        r = pytan.utils.parse_defs(
            defname='question_option_defs',
            deftypes=['dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertFalse(r)

    def test_parse_emptystr(self):
        kwargs = {'question_option_defs': ''}
        r = pytan.utils.parse_defs(
            defname='question_option_defs',
            deftypes=['dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertFalse(r)

    def test_parse_emptylist(self):
        kwargs = {'question_option_defs': []}
        r = pytan.utils.parse_defs(
            defname='question_option_defs',
            deftypes=['dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertFalse(r)

    def test_parse_emptydict(self):
        kwargs = {'question_option_defs': {}}
        r = pytan.utils.parse_defs(
            defname='question_option_defs',
            deftypes=['dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertFalse(r)

    def test_parse_options_dict(self):
        kwargs = {'question_option_defs': {
            'all_values_flag': 0,
            'ignore_case_flag': 1,
            'max_age_seconds': '3600',
            'value_type': 'string',
            'all_times_flag': 0
        }}
        r = pytan.utils.parse_defs(
            defname='question_option_defs',
            deftypes=['dict()'],
            empty_ok=True,
            **kwargs
        )
        self.assertEquals(r, kwargs['question_option_defs'])

    def test_parse_str(self):
        e = (
            "'question_option_defs' requires a non-empty value of type:"
            " dict\(\)"
        )
        kwargs = {'question_option_defs': 'no string allowed'}
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            pytan.utils.parse_defs(
                defname='question_option_defs',
                deftypes=['dict()'],
                empty_ok=True,
                **kwargs
            )

    def test_parse_list(self):
        e = (
            "'question_option_defs' requires a non-empty value of type:"
            " dict\(\)"
        )
        kwargs = {'question_option_defs': ['no list allowed']}
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            pytan.utils.parse_defs(
                defname='question_option_defs',
                deftypes=['dict()'],
                empty_ok=True,
                **kwargs
            )


class TestManualPackageDefValidateUtils(unittest.TestCase):
    def test_valid1(self):
        kwargs = {'package_def': {'name': 'Package1'}}
        pytan.utils.val_package_def(**kwargs)

    def test_valid2(self):
        kwargs = {'package_def': {
            'name': 'Package1',
            'params': {'dirname': 'Program Files'},
        }}
        pytan.utils.val_package_def(**kwargs)

    def test_invalid1(self):
        e = "Package definition.*missing one of id, name!"
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            kwargs = {'package_def': {'NONAME': 'Package1'}}
            pytan.utils.val_package_def(**kwargs)

    def test_invalid2(self):
        e = "Package definition.*has more than one of id, name!"
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            kwargs = {'package_def': {'name': 'test1', 'id': '2'}}
            pytan.utils.val_package_def(**kwargs)


class TestManualSensorDefValidateUtils(unittest.TestCase):
    def test_valid1(self):
        kwargs = {'sensor_defs': [{'name': 'Sensor1'}]}
        pytan.utils.val_sensor_defs(**kwargs)

    def test_valid2(self):
        kwargs = {'sensor_defs': [
            {
                'name': 'Sensor1',
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*'
                },
            }
        ]}
        pytan.utils.val_sensor_defs(**kwargs)

    def test_valid3(self):
        kwargs = {'sensor_defs': [
            {
                'name': 'Sensor1',
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*'
                },
                'options': {
                    'all_values_flag': 0,
                    'ignore_case_flag': 1,
                    'max_age_seconds': '3600',
                    'value_type': 'string',
                    'all_times_flag': 0
                },
            }
        ]}
        pytan.utils.val_sensor_defs(**kwargs)

    def test_valid4(self):
        kwargs = {'sensor_defs': [{'name': 'test1', 'filter': {'n': 'k'}}]}
        pytan.utils.val_sensor_defs(**kwargs)

    def test_invalid1(self):
        e = "Sensor definition.*missing one of id, name, hash!"
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            kwargs = {'sensor_defs': [{'NONAME': 'Sensor1'}]}
            pytan.utils.val_sensor_defs(**kwargs)

    def test_invalid2(self):
        e = "Sensor definition.*missing one of id, name, hash!"
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            kwargs = {'sensor_defs': [{}]}
            pytan.utils.val_sensor_defs(**kwargs)

    def test_invalid3(self):
        if sys.version_info < (3, 0):
            e = (
                "'filter' key in definition dictionary must be a \[<type 'dict'>\]"
                ", you supplied a <type 'list'>!"
            )
        else:
            e = (
                "'filter' key in definition dictionary must be a \[<class 'dict'>\]"
                ", you supplied a <class 'list'>!"
            )
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            kwargs = {'sensor_defs': [{'name': 'test1', 'filter': [{}]}]}
            pytan.utils.val_sensor_defs(**kwargs)

    def test_invalid4(self):
        e = "Sensor definition.*has more than one of id, name, hash!"
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            kwargs = {'sensor_defs': [{'name': 'test1', 'id': '2'}]}
            pytan.utils.val_sensor_defs(**kwargs)


class TestManualQuestionFilterDefValidateUtils(unittest.TestCase):
    def test_valid1(self):
        kwargs = {'q_filter_defs': [
            {
                'name': 'Sensor1',
                'filter': {
                    'operator': 'RegexMatch',
                    'not_flag': 0,
                    'value': '.*'
                },
            }
        ]}
        pytan.utils.val_q_filter_defs(**kwargs)

    def test_valid2(self):
        kwargs = {'q_filter_defs': []}
        pytan.utils.val_q_filter_defs(**kwargs)

    def test_invalid1(self):
        e = "Definition.*missing 'filter' key!"
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            kwargs = {'q_filter_defs': [{'name': 'Sensor1'}]}
            pytan.utils.val_q_filter_defs(**kwargs)


class TestManualBuildObjectUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls): # noqa
        # load in our JSON sensor object for testing
        f = os.path.join(my_dir, 'sensor_obj_with_params.json')
        cls.sensor_obj_with_params = pytan.utils.load_taniumpy_from_json(f)

        f = os.path.join(my_dir, 'sensor_obj_no_params.json')
        cls.sensor_obj_no_params = pytan.utils.load_taniumpy_from_json(f)

    def test_build_selectlist_obj_noparamssensorobj_noparams(self):
        '''builds a selectlist object using a sensor obj with no params'''

        sensor_defs = [
            {
                'name': 'Fake Sensor',
                'filter': {
                    'operator': 'regexmatch',
                    'not_flag': 0,
                    'value': '.*'
                },
                'options': {
                    'all_values_flag': 0,
                    'ignore_case_flag': 1,
                    'max_age_seconds': '3600',
                    'value_type': 'string',
                    'all_times_flag': 0,
                    'ignored_option': 'tt',
                },
                'sensor_obj': self.sensor_obj_no_params
            }
        ]

        kwargs = {'sensor_defs': sensor_defs}

        r = pytan.utils.build_selectlist_obj(**kwargs)

        self.assertIsInstance(r, taniumpy.SelectList)
        self.assertIsInstance(r.select[0], taniumpy.Select)
        self.assertEqual(len(r.select), 1)
        self.assertIsInstance(r.select[0].filter, taniumpy.Filter)
        self.assertIsInstance(r.select[0].sensor, taniumpy.Sensor)
        self.assertEqual(
            r.select[0].sensor.hash, self.sensor_obj_no_params.hash)
        self.assertEqual(
            r.select[0].filter.sensor.hash, self.sensor_obj_no_params.hash)
        self.assertIsNone(r.select[0].sensor.parameters)
        self.assertEqual(r.select[0].filter.operator, 'RegexMatch')
        self.assertEqual(r.select[0].filter.not_flag, 0)
        self.assertEqual(r.select[0].filter.value, '.*')
        self.assertEqual(r.select[0].filter.all_values_flag, 0)
        self.assertEqual(r.select[0].filter.ignore_case_flag, 1)
        self.assertEqual(r.select[0].filter.max_age_seconds, 3600)
        self.assertEqual(r.select[0].filter.value_type, 'String')
        self.assertEqual(r.select[0].filter.all_times_flag, 0)
        self.assertFalse(hasattr(r.select[0].filter, 'ignored_option'))

    def test_build_selectlist_obj_noparamssensorobj_withparams(self):
        '''builds a selectlist object using a sensor obj with no params,
        but passing in params (which should be added as of 1.0.4)'''

        sensor_defs = [
            {
                'name': 'Fake Sensor',
                'filter': {
                    'operator': 'regexmatch',
                    'not_flag': 0,
                    'value': '.*'
                },
                'params': {
                    'dirname': 'Program Files',
                },
                'options': {
                    'all_values_flag': 0,
                    'ignore_case_flag': 1,
                    'max_age_seconds': '3600',
                    'value_type': 'string',
                    'all_times_flag': 0,
                    'ignored_option': 'tt',
                },
                'sensor_obj': self.sensor_obj_no_params
            }
        ]

        kwargs = {'sensor_defs': sensor_defs}

        r = pytan.utils.build_selectlist_obj(**kwargs)
        self.assertIsInstance(r, taniumpy.SelectList)
        self.assertIsInstance(r.select[0], taniumpy.Select)
        self.assertEqual(len(r.select), 1)
        self.assertIsInstance(r.select[0].filter, taniumpy.Filter)
        self.assertIsInstance(r.select[0].sensor, taniumpy.Sensor)
        self.assertEqual(
            r.select[0].sensor.source_id, self.sensor_obj_no_params.id)
        self.assertEqual(
            r.select[0].filter.sensor.id, self.sensor_obj_no_params.id)
        self.assertTrue(r.select[0].sensor.parameters)
        self.assertEqual(r.select[0].filter.operator, 'RegexMatch')
        self.assertEqual(r.select[0].filter.not_flag, 0)
        self.assertEqual(r.select[0].filter.value, '.*')
        self.assertEqual(r.select[0].filter.all_values_flag, 0)
        self.assertEqual(r.select[0].filter.ignore_case_flag, 1)
        self.assertEqual(r.select[0].filter.max_age_seconds, 3600)
        self.assertEqual(r.select[0].filter.value_type, 'String')
        self.assertEqual(r.select[0].filter.all_times_flag, 0)
        self.assertFalse(hasattr(r.select[0].filter, 'ignored_option'))

    def test_build_selectlist_obj_withparamssensorobj_noparams(self):
        '''builds a selectlist object using a sensor obj with 4 params
        but not supplying any values for any of the params'''

        sensor_defs = [
            {
                'name': 'Fake Sensor',
                'filter': {
                    'operator': 'regexmatch',
                    'not_flag': 0,
                    'value': '.*'
                },
                'options': {
                    'all_values_flag': 0,
                    'ignore_case_flag': 1,
                    'max_age_seconds': '3600',
                    'value_type': 'string',
                    'all_times_flag': 0,
                    'ignored_option': 'tt',
                },
                'sensor_obj': self.sensor_obj_with_params
            }
        ]

        kwargs = {'sensor_defs': sensor_defs}

        r = pytan.utils.build_selectlist_obj(**kwargs)

        self.assertIsInstance(r, taniumpy.SelectList)
        self.assertIsInstance(r.select[0], taniumpy.Select)
        self.assertEqual(len(r.select), 1)
        self.assertIsInstance(r.select[0].filter, taniumpy.Filter)
        self.assertIsInstance(r.select[0].sensor, taniumpy.Sensor)
        self.assertEqual(
            r.select[0].sensor.source_id, self.sensor_obj_with_params.id)
        self.assertEqual(
            r.select[0].filter.sensor.id, self.sensor_obj_with_params.id)
        self.assertEqual(len(r.select[0].sensor.parameters), 4)
        for x in r.select[0].sensor.parameters:
            self.assertRegexpMatches(x.key, '||.*||')
            if x.key == '||dirname||':
                self.assertEqual(x.value, '')
            if x.key == '||regexp||':
                self.assertEqual(x.value, '')
            if x.key == '||casesensitive||':
                self.assertEqual(x.value, 'No')
            if x.key == '||global||':
                self.assertEqual(x.value, 'No')

        self.assertEqual(r.select[0].filter.operator, 'RegexMatch')
        self.assertEqual(r.select[0].filter.not_flag, 0)
        self.assertEqual(r.select[0].filter.value, '.*')
        self.assertEqual(r.select[0].filter.all_values_flag, 0)
        self.assertEqual(r.select[0].filter.ignore_case_flag, 1)
        self.assertEqual(r.select[0].filter.max_age_seconds, 3600)
        self.assertEqual(r.select[0].filter.value_type, 'String')
        self.assertEqual(r.select[0].filter.all_times_flag, 0)
        self.assertFalse(hasattr(r.select[0].filter, 'ignored_option'))

    def test_build_selectlist_obj_withparamssensorobj_withparams(self):
        '''builds a selectlist object using a sensor obj with 4 params
        but supplying a value for only one param'''

        sensor_defs = [
            {
                'name': 'Fake Sensor',
                'filter': {
                    'operator': 'regexmatch',
                    'not_flag': 0,
                    'value': '.*'
                },
                'params': {
                    'dirname': 'Program Files',
                },
                'options': {
                    'all_values_flag': 0,
                    'ignore_case_flag': 1,
                    'max_age_seconds': '3600',
                    'value_type': 'string',
                    'all_times_flag': 0,
                    'ignored_option': 'tt',
                },
                'sensor_obj': self.sensor_obj_with_params
            }
        ]

        kwargs = {'sensor_defs': sensor_defs}

        r = pytan.utils.build_selectlist_obj(**kwargs)

        self.assertIsInstance(r, taniumpy.SelectList)
        self.assertIsInstance(r.select[0], taniumpy.Select)
        self.assertEqual(len(r.select), 1)
        self.assertIsInstance(r.select[0].filter, taniumpy.Filter)
        self.assertIsInstance(r.select[0].sensor, taniumpy.Sensor)
        self.assertEqual(
            r.select[0].sensor.source_id, self.sensor_obj_with_params.id)
        self.assertEqual(
            r.select[0].filter.sensor.id, self.sensor_obj_with_params.id)

        self.assertEqual(len(r.select[0].sensor.parameters), 4)
        for x in r.select[0].sensor.parameters:
            self.assertRegexpMatches(x.key, '||.*||')
            if x.key == '||dirname||':
                self.assertEqual(x.value, 'Program Files')
            if x.key == '||regexp||':
                self.assertEqual(x.value, '')
            if x.key == '||casesensitive||':
                self.assertEqual(x.value, 'No')
            if x.key == '||global||':
                self.assertEqual(x.value, 'No')

        self.assertEqual(r.select[0].filter.operator, 'RegexMatch')
        self.assertEqual(r.select[0].filter.not_flag, 0)
        self.assertEqual(r.select[0].filter.value, '.*')
        self.assertEqual(r.select[0].filter.all_values_flag, 0)
        self.assertEqual(r.select[0].filter.ignore_case_flag, 1)
        self.assertEqual(r.select[0].filter.max_age_seconds, 3600)
        self.assertEqual(r.select[0].filter.value_type, 'String')
        self.assertEqual(r.select[0].filter.all_times_flag, 0)
        self.assertFalse(hasattr(r.select[0].filter, 'ignored_option'))

    def test_build_group_obj(self):

        q_filter_defs = [
            {
                'name': 'Fake Sensor',
                'filter': {
                    'operator': 'regexmatch',
                    'not_flag': 0,
                    'value': '.*'
                },
                'sensor_obj': self.sensor_obj_no_params
            }
        ]

        q_option_defs = {
            'all_values_flag': 0,
            'ignore_case_flag': 1,
            'max_age_seconds': '3600',
            'value_type': 'string',
            'all_times_flag': 0,
            'and_flag': 1,
            'ignored_option': 'tt',
        }

        kwargs = {
            'q_filter_defs': q_filter_defs,
            'q_option_defs': q_option_defs,
        }

        r = pytan.utils.build_group_obj(**kwargs)

        self.assertIsInstance(r, taniumpy.Group)
        self.assertIsInstance(r.filters, taniumpy.FilterList)
        self.assertEqual(len(r.filters), 1)
        self.assertIsInstance(r.filters[0], taniumpy.Filter)
        self.assertEqual(
            r.filters[0].sensor.hash, self.sensor_obj_no_params.hash)
        self.assertEqual(r.filters[0].operator, 'RegexMatch')
        self.assertEqual(r.filters[0].not_flag, 0)
        self.assertEqual(r.filters[0].value, '.*')
        self.assertEqual(r.filters[0].all_values_flag, 0)
        self.assertEqual(r.filters[0].ignore_case_flag, 1)
        self.assertEqual(r.filters[0].max_age_seconds, 3600)
        self.assertEqual(r.filters[0].value_type, 'String')
        self.assertEqual(r.filters[0].all_times_flag, 0)
        self.assertFalse(hasattr(r.filters[0], 'ignored_option'))

    def test_build_manual_q(self):
        r = pytan.utils.build_manual_q(taniumpy.SelectList(), taniumpy.Group())
        self.assertIsInstance(r, taniumpy.Question)
        self.assertIsInstance(r.group, taniumpy.Group)
        self.assertIsInstance(r.selects, taniumpy.SelectList)

    def test_build_selectlist_obj_invalid_filter(self):

        sensor_defs = [
            {
                'name': 'Fake Sensor',
                'filter': {
                    'operator': 'egexMatch',
                    'value': '.*'
                },
                'sensor_obj': self.sensor_obj_no_params
            }
        ]

        kwargs = {'sensor_defs': sensor_defs}
        e = "Invalid filter.*"
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            pytan.utils.build_selectlist_obj(**kwargs)

    def test_build_selectlist_obj_missing_value(self):
        sensor_defs = [
            {
                'name': 'Fake Sensor',
                'filter': {
                    'operator': 'RegexMatch',
                },
                'sensor_obj': self.sensor_obj_no_params
            }
        ]

        kwargs = {'sensor_defs': sensor_defs}
        e = ".*requires a 'value' key!"
        with self.assertRaisesRegexp(pytan.exceptions.DefinitionParserError, e):
            pytan.utils.build_selectlist_obj(**kwargs)


class TestGenericUtils(unittest.TestCase):
    def test_is_list(self):
        self.assertTrue(pytan.utils.is_list([]))

    def test_is_not_list(self):
        self.assertFalse(pytan.utils.is_list(''))

    def test_is_str(self):
        self.assertTrue(pytan.utils.is_str(''))

    def test_is_not_str(self):
        self.assertFalse(pytan.utils.is_str([]))

    def test_is_dict(self):
        self.assertTrue(pytan.utils.is_dict({}))

    def test_is_not_dict(self):
        self.assertFalse(pytan.utils.is_dict([]))

    def test_is_num(self):
        self.assertTrue(pytan.utils.is_num(2))

    def test_is_not_num(self):
        self.assertFalse(pytan.utils.is_num({}))

    def test_version_lower(self):
        self.assertTrue(pytan.binsupport.version_check('0.0.0'))

    def test_get_now(self):
        self.assertTrue(pytan.utils.get_now())

    def test_jsonify(self):
        exp = '{\n  "x": "d"\n}'
        self.assertEquals(pytan.utils.jsonify({'x': 'd'}), exp)

    def test_invalid_port(self):
        self.assertFalse(pytan.utils.port_check('localhost', 1, 0))

    def test_version_higher(self):
        req_ver = "9.9.9"
        e = (
            "Script and API Version mismatch.*version {}, required {}"
        ).format(pytan.__version__, req_ver)
        with self.assertRaisesRegexp(Exception, e):
            pytan.binsupport.version_check(req_ver)

    def test_empty_obj(self):
        obj = taniumpy.SensorList()
        self.assertTrue(pytan.utils.empty_obj(obj))
        self.assertTrue(pytan.utils.empty_obj(''))

    def test_get_q_obj_map(self):
        qtype = 'saved'
        self.assertEqual(pytan.utils.get_q_obj_map(qtype), {'handler': 'ask_saved'})

        qtype = 'manual'
        self.assertEqual(pytan.utils.get_q_obj_map(qtype), {'handler': 'ask_manual'})

        qtype = '_manual'
        self.assertEqual(
            pytan.utils.get_q_obj_map(qtype), {'handler': '_ask_manual'})

        qtype = ''
        e = (
            ".*not a valid question type, must be one of.*"
        )
        with self.assertRaisesRegexp(pytan.exceptions.HandlerError, e):
            pytan.utils.get_q_obj_map(qtype)

        qtype = 'invalid'
        e = (
            ".*not a valid question type, must be one of.*"
        )
        with self.assertRaisesRegexp(pytan.exceptions.HandlerError, e):
            pytan.utils.get_q_obj_map(qtype)

    def test_load_taniumpy_file_invalid_file(self):
        f = 'invalid_file.1234'
        with self.assertRaises(pytan.exceptions.HandlerError):
            pytan.utils.load_taniumpy_from_json(f)

    def test_load_taniumpy_file_invalid_json(self):
        f = os.path.join(root_dir, 'doc/example_of_all_package_parameters.json')
        with self.assertRaises(pytan.exceptions.HandlerError):
            pytan.utils.load_taniumpy_from_json(f)

    def test_load_param_file_valid(self):
        f = os.path.join(root_dir, 'doc/example_of_all_package_parameters.json')
        z = pytan.utils.load_param_json_file(f)
        self.assertIn('ParametersArray', z)

    def test_load_param_file_invalid_file(self):
        f = 'invalid_file.1234'
        with self.assertRaises(pytan.exceptions.HandlerError):
            pytan.utils.load_param_json_file(f)

    def test_load_param_file_invalid_json(self):
        f = os.path.join(my_dir, 'sensor_obj_no_params.json')
        with self.assertRaises(pytan.exceptions.HandlerError):
            pytan.utils.load_param_json_file(f)

    def test_get_obj_map(self):
        obj = 'sensor'
        exp = {
            'single': 'Sensor',
            'multi': 'SensorList',
            'all': 'SensorList',
            'search': ['id', 'name', 'hash'],
            'manual': False,
            'delete': True,
            'create_json': True,
        }
        self.assertEqual(pytan.utils.get_obj_map(obj), exp)

        obj = 'invalid'
        e = (
            ".*not a valid object to get, must be one of.*"
        )
        with self.assertRaisesRegexp(pytan.exceptions.HandlerError, e):
            pytan.utils.get_obj_map(obj)


class TestDeserializeBadXML(unittest.TestCase):
    def test_bad_chars_basetype_control(self):
        '''
        This XML file has a number of control characters that are not valid in XML.

        This test validates that pytan.xml_clean.xml_cleaner() will remove all the invalid
        and restricted characters, which should allow the body to be parsed properly.
        '''
        '''
        Logging examples from xml_cleaner():
        v=open('bad_chars_basetype_control.xml').read()
        >>> pytan.xml_clean.xml_cleaner(v, show_bad_characters=True)
        XMLCleaner: Replaced 4 invalid characters that did not match the regex u'[^\t\n\r -\ud7ff\ue000-\ufffd]'
        XMLCleaner: Invalid characters found: [u'\x17', u'\x04', u'\x04', u'\x01']
        XMLCleaner: Replaced 10 restricted characters that did not match the regex u'[\x7f-\x84\x86-\x9f\ufdd0-\ufdef]'
        XMLCleaner: Restricted characters found: [u'\x80', u'\x80', u'\x8d', u'\x95', u'\x81', u'\x89', u'\x89', u'\x81', u'\x95', u'\x8b']
        '''
        f = 'bad_chars_basetype_control.xml'
        a = open(os.path.join(my_dir, f), 'rb+').read()
        b = pytan.xml_clean.xml_cleaner(a, log_messages=False)
        c = pytan.taniumpy.BaseType.fromSOAPBody(b)
        self.assertTrue(c)
        self.assertIsInstance(c, taniumpy.SystemStatusList)

    def test_bad_chars_resultset_latin1(self):
        '''
        This XML file has some characters that are actually encoded as latin1 (as well as some
        restricted characters).

        This test validates that pytan.xml_clean.xml_cleaner() will properly fall back to latin1
        for decoding the docuemnt, as well as remove all the invalid and restricted characters,
        which should allow the body to be parsed properly.
        '''
        '''
        Logging examples from xml_cleaner():
        >>> v=open('bad_chars_resultset_latin1.xml').read()
        >>> pytan.xml_clean.xml_cleaner(v, show_bad_characters=True)
        XMLCleaner: Falling back to latin1 for decoding, unable to decode as UTF-8!
        XMLCleaner: No invalid characters found
        XMLCleaner: Replaced 2 restricted characters that did not match the regex u'[\x7f-\x84\x86-\x9f\ufdd0-\ufdef]'
        XMLCleaner: Restricted characters found: [u'\x93', u'\x94']
        '''
        f = 'bad_chars_resultset_latin1.xml'
        a = open(os.path.join(my_dir, f), 'rb+').read()
        b = pytan.xml_clean.xml_cleaner(a, log_messages=False)
        el = ET.fromstring(b)
        cdata = el.find('.//ResultXML')
        rd = ET.fromstring(cdata.text)
        c = pytan.taniumpy.ResultSet.fromSOAPElement(rd)
        self.assertTrue(c)
        self.assertIsInstance(c, taniumpy.ResultSet)

    def test_bad_chars_resultset_surrogate(self):
        '''
        This XML file has some characters that are unpaired surrogates in unicode. Surrogates
        (unpaired or otherwise) are not legal XML characters.

        This test validates that pytan.xml_clean.xml_cleaner() will properly remove all the
        invalid and restricted characters, which should allow the body to be parsed properly.
        '''
        '''
        Logging examples from xml_cleaner():
        >>> v=open('bad_chars_resultset_surrogate.xml').read()
        >>> pytan.xml_clean.xml_cleaner(v, show_bad_characters=True)
        XMLCleaner: Replaced 1 invalid characters that did not match the regex u'[^\t\n\r -\ud7ff\ue000-\ufffd]'
        XMLCleaner: Invalid characters found: [u'\ude64']
        XMLCleaner: No restricted characters found
        '''
        f = 'bad_chars_resultset_surrogate.xml'
        a = open(os.path.join(my_dir, f), 'rb+').read()
        b = pytan.xml_clean.xml_cleaner(a, log_messages=False)
        el = ET.fromstring(b)
        cdata = el.find('.//ResultXML')
        rd = ET.fromstring(cdata.text)
        c = pytan.taniumpy.ResultSet.fromSOAPElement(rd)
        self.assertTrue(c)
        self.assertIsInstance(c, taniumpy.ResultSet)

'''
# debug path for checking open file handles, ensuring
import atexit


@atexit.register
def get_open_fds():
    import subprocess
    import os

    pid = os.getpid()
    procs = subprocess.check_output(["lsof", '-w', "-p", str(pid)])
    print procs

    procs = subprocess.check_output(["lsof", '-w', '-Ff', "-p", str(pid)])

    proc_defs = filter(
        lambda s: s and s[0] == 'f' and s[1:].isdigit(),
        procs.split('\n')
    )

    nprocs = len(proc_defs)
    print "{} number of open FDs".format(nprocs)
    for p in proc_defs:
        print p
    return nprocs
'''

if __name__ == "__main__":
    unittest.main(
        verbosity=SERVER_INFO["testlevel"],
        failfast=SERVER_INFO["FAILFAST"],
        catchbreak=SERVER_INFO["CATCHBREAK"],
        buffer=SERVER_INFO["BUFFER"],
    )
