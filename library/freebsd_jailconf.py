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


# These are the core parameters that are passed to the kernel. Descriptions for
# the first one or two sentences from the jail(8) man page.
JAIL_CORE_PARAMETERS = (
    {
        'name': 'name',
        'required': True,
        'description': ('The jail name. This is an arbitrary string that '
                        'identifies a jail (except it may not contain a ".").'),
        'type': 'str',
    },
    {
        'name': 'path',
        'description': 'The directory which is to be the root of the jail.',
    },
    {
        'name': 'ip4.addr',
        'description': 'A list of IPv4 addresses assigned to the jail.',
    },
    {
        'name': 'ip4.saddrsel',
        'description': ('A boolean option to disable IPv4 source address '
                        'selection for the jail in favour of the primary IPv4 '
                        'address of the jail.'),
        'type': 'bool'
    },
    {
        'name': 'ip4',
        'description': 'Control the availability of IPv4 addresses.',
    },
    {
        'name': 'ip6.addr',
        'description': '',
    },
    {
        'name': 'ip6.saddrsel',
        'description': '',
    },
    {
        'name': 'ip6',
        'description': '',
    },
    {
        'name': 'vnet',
        'description': '',
    },
    {
        'name': 'host.hostname',
        'description': '',
    },
    {
        'name': 'host',
        'description': '',
    },
    {
        'name': 'securelevel',
        'description': '',
    },
    {
        'name': 'devfs_ruleset',
        'description': '',
    },
    {
        'name': 'children.max',
        'description': '',
    },
    {
        'name': 'children.cur',
        'description': '',
    },
    {
        'name': 'enforce_statfs',
        'description': '',
    },
    {
        'name': 'persist',
        'description': '',
    },
    {
        'name': 'osrelease',
        'description': '',
    },
    {
        'name': 'osreldate',
        'description': '',
    },
    {
        'name': 'allow.set_hostname',
        'description': '',
    },
    {
        'name': 'allow.sysvipc',
        'description': '',
    },
    {
        'name': 'allow.raw_sockets',
        'description': '',
    },
    {
        'name': 'allow.chflags',
        'description': '',
    },
    {
        'name': 'allow.mount',
        'description': '',
    },
    {
        'name': 'allow.mount.devfs',
        'description': '',
    },
    {
        'name': 'allow.mount.fdescfs',
        'description': '',
    },
    {
        'name': 'allow.mount.nullfs',
        'description': '',
    },
    {
        'name': 'allow.mount.procfs',
        'description': '',
    },
    {
        'name': 'allow.mount.linprocfs',
        'description': '',
    },
    {
        'name': 'allow.mount.linsysfs',
        'description': '',
    },
    {
        'name': 'allow.mount.tmpfs',
        'description': '',
    },
    {
        'name': 'allow.mount.zfs',
        'description': '',
    },
    {
        'name': 'allow.quotas',
        'description': '',
    },
    {
        'name': 'allow.socket_af',
        'description': '',
    },
    {
        'name': 'linux',
        'description': '',
    },
    {
        'name': 'linux.osname',
        'description': '',
    },
    {
        'name': 'linux.osrelease',
        'description': '',
    },
    {
        'name': 'linux.oss_version',
        'description': '',
    },
    {
        'name': 'sysvmsg',
        'description': '',
    },
    {
        'name': 'sysvsem',
        'description': '',
    },
    {
        'name': 'sysvshm',
        'description': '',
    },
)

# These parameters are only used by jail(8).
JAIL_PSUEDO_PARAMETERS = (
    {
        'name': 'exec.prestart',
        'description': '',
    },
    {
        'name': 'exec.start',
        'description': '',
    },
    {
        'name': 'command',
        'description': '',
    },
    {
        'name': 'exec.poststart',
        'description': '',
    },
    {
        'name': 'exec.prestop',
        'description': '',
    },
    {
        'name': 'exec.stop',
        'description': '',
    },
    {
        'name': 'exec.poststop',
        'description': '',
    },
    {
        'name': 'exec.clean',
        'description': '',
    },
    {
        'name': 'exec.jail_user',
        'description': '',
    },
    {
        'name': 'exec.system_jail_user',
        'description': '',
    },
    {
        'name': 'exec.system_user',
        'description': '',
    },
    {
        'name': 'exec.timeout',
        'description': '',
    },
    {
        'name': 'exec.consolelog',
        'description': '',
    },
    {
        'name': 'exec.fib',
        'description': '',
    },
    {
        'name': 'stop.timeout',
        'description': '',
    },
    {
        'name': 'interface',
        'description': '',
    },
    {
        'name': 'vnet.interface',
        'description': '',
    },
    {
        'name': 'ip_hostname',
        'description': '',
    },
    {
        'name': 'mount',
        'description': '',
    },
    {
        'name': 'mount.fstab',
        'description': '',
    },
    {
        'name': 'mount.devfs',
        'description': '',
    },
    {
        'name': 'mount.fdescfs',
        'description': '',
    },
    {
        'name': 'mount.procfs',
        'description': '',
    },
    {
        'name': 'allow.dying',
        'description': '',
    },
    {
        'name': 'depend',
        'description': '',
    },
)

from itertools import chain
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

    for parameter in chain(JAIL_CORE_PARAMETERS, JAIL_PSUEDO_PARAMETERS):
        param_options = parameter.copy()
        option_name = param_options['name']
        del param_options['name']
        if 'type' not in param_options:
            param_options['type'] = 'str'
        module_args[option_name] = param_options

    result = dict(
        changed=False,
        original_message='',
        message='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[('state', 'present', ('path',))],
        supports_check_mode=False
    )

    jail = FreeBsdJail(module)
    jail.load()

    module.exit_json(**result)


if __name__ == '__main__':
    main()
