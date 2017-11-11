#!/usr/bin/env python2


from __future__ import absolute_import, division, print_function


DOCUMENTATION = '''
'''


EXAMPLES = '''
'''


RETURN = '''
'''

import textwrap
import sys

from ansible.module_utils.basic import AnsibleModule

from pyparsing import Combine, Dict, Group, Literal, Word, ZeroOrMore, alphas, \
    alphanums, cppStyleComment, dblQuotedString, delimitedList, \
    pythonStyleComment, restOfLine, sglQuotedString


class FreeBsdJail(object):

    def __init__(self, module):
        self.conf_file = module.params['conf_file']

    def parser(self):
        word = Word(alphanums)
        token = Word(alphanums + '-_.:')
        path = Word(alphanums + '-_.:/')

        end = Literal(';').suppress()

        jail_name = delimitedList(Word(alphanums + '-.*'), delim='.', combine=True)

        boolean_parameter = token + end
        value = dblQuotedString | sglQuotedString | delimitedList(token) | path
        parameter = token + (Literal('=') | Literal('+=')) + value + end

        variable = Combine('$' + word) | Combine('$' + '{' + token + '}')
        variable_definition = variable + '=' + (dblQuotedString | sglQuotedString | path) + end

        jail_def = (
            jail_name + Literal('{') +
            ZeroOrMore(Group(boolean_parameter | parameter | variable_definition)) +
            Literal('}')
        )

        jail = Dict(ZeroOrMore(Group(jail_def | boolean_parameter | parameter)))
        jail.ignore(cppStyleComment)
        jail.ignore(pythonStyleComment)
        return jail


def main():

    module_args = {
        'name': {
            'required': True,
            'type': 'str',
        },
        'conf_file': {
            'default': '/etc/jail.conf',
            'required': False,
            'type': 'str',
        },
        'state': {
            'choices': ['present', 'absent'],
            'default': 'present',
            'type': 'str',
        },
    }

    result = dict(
        changed=False,
        original_message='',
        message='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    jail = FreeBsdJail(module)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
