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


def jail_parser():
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


def demo_jail():
    return textwrap.dedent("""\
        # Typical static defaults:
        # Use the rc scripts to start and stop jails.  Mount jail's /dev.
        exec.start	= "/bin/sh /etc/rc";
        exec.stop = "/bin/sh /etc/rc.shutdown";
        exec.clean;
        mount.devfs;

        # Dynamic wildcard	parameter:
        # Base the	path off the jail name.
        path = "/var/jail/$name";

        # A typical jail.
        foo {
                host.hostname = "foo.com";
                ip4.addr =	10.1.1.1, 10.1.1.2, 10.1.1.3;
        }

        # This jail overrides the defaults	defined	above.
        bar {
                exec.start	= '';
                exec.stop = '';
                path = /;
                mount.nodevfs;
                persist;	     //	Required because there are no processes
        }

        * {
            path = "/jail/$name";
        }

        a.b.* {
            path = "/jail/$name";
            path = "/jail/$name";
        }
    """)

def main(args):

    jail = jail_parser()

    for jail_file in (demo_jail(), ):
        #jail_conf = jail.parseFile(jail_file)
        jail_conf = jail.parseString(jail_file)
        print("In:")
        print(jail_file)
        print("Out:")
        print(jail_conf)
        print(jail_conf.asDict())


if __name__ == '__main__':
    main(sys.argv)
