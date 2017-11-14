#!/usr/bin/env python2


from __future__ import absolute_import, division, print_function


DOCUMENTATION = '''
---
author:
  - Sean Kelly
module: freebsd_jailconf
short_description: Configure FreeBSD's jail.conf
requirements:
  - This module requires pyparsing.
options:
  name:
    description: Name of the jail. Use an empty string ('') to set global options.
    required: True
  conf_file:
    description: Path to the jail.conf file.
    default: /etc/jail.conf
  state:
    description: Create or delete a jail or option.
    choices: ['present', 'absent']
    default: present
'''


EXAMPLES = '''
'''


RETURN = '''
'''


# These are the core parameters that are passed to the kernel.
JAIL_CORE_PARAMETERS = (
    'jid',
    'name',
    'path',
    'ip4.addr',
    'ip4.saddrsel',
    'ip4',
    'ip6.addr',
    'ip6.saddrsel',
    'ip6',
    'vnet',
    'host.hostname',
    'host',
    'securelevel',
    'devfs_ruleset',
    'children.max',
    'children.cur',
    'enforce_statfs',
    'persist',
    'osrelease',
    'osreldate',
    'allow.set_hostname',
    'allow.sysvipc',
    'allow.raw_sockets',
    'allow.chflags',
    'allow.mount',
    'allow.mount.devfs',
    'allow.mount.fdescfs',
    'allow.mount.nullfs',
    'allow.mount.procfs',
    'allow.mount.linprocfs',
    'allow.mount.linsysfs',
    'allow.mount.tmpfs',
    'allow.mount.zfs',
    'allow.quotas',
    'allow.socket_af',
    'linux',
    'linux.osname',
    'linux.osrelease',
    'linux.oss_version',
    'sysvmsg',
    'sysvsem',
    'sysvshm',
)

# These parameters are only used by jail(8).
JAIL_PSUEDO_PARAMETERS = (
    'exec.prestart',
    'exec.start',
    'command',
    'exec.poststart',
    'exec.prestop',
    'exec.stop',
    'exec.poststop',
    'exec.clean',
    'exec.jail_user',
    'exec.system_jail_user',
    'exec.system_user',
    'exec.timeout',
    'exec.consolelog',
    'exec.fib',
    'stop.timeout',
    'interface',
    'vnet.interface',
    'ip_hostname',
    'mount',
    'mount.fstab',
    'mount.devfs',
    'mount.fdescfs',
    'mount.procfs',
    'allow.dying',
    'depend',
)

import textwrap
import sys

from ansible.module_utils.basic import AnsibleModule

from pyparsing import Combine, Dict, Group, Literal, Word, ZeroOrMore, alphas, \
    alphanums, cppStyleComment, dblQuotedString, delimitedList, \
    pythonStyleComment, restOfLine, sglQuotedString


class FreeBsdJail(object):

    def __init__(self, module):
        self.conf_file = module.params['conf_file']
        self.parser = self.jail_parser()
        self.jail = None

    def jail_parser(self):
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

    def load(self):
        self.jail = self.parser.parseFile(self.conf_file, parseAll=True)


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
    jail.load()

    module.exit_json(**result)


if __name__ == '__main__':
    main()
