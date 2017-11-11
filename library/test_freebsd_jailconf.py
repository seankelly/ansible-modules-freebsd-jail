
import json

from ansible.compat.tests import unittest
from ansible.compat.tests.mock import patch
from ansible.module_utils import basic
from ansible.module_utils.six.moves import builtins
from ansible.module_utils._text import to_bytes

import freebsd_jailconf


class AnsibleFail(Exception):
    pass


class AnsibleExit(Exception):
    pass


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


def exit_json(*args, **kwargs):
    kwargs['failed'] = True
    return kwargs


def fail_json(*args, **kwargs):
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    return kwargs


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


class TestJailConf(unittest.TestCase):
    def setUp(self):
        self.module = freebsd_jailconf

    def execute_module(self, failed=False, changed=False):
        def open_file(file_path):
            pass

        def run(method, func):
            with patch.object(basic.AnsibleModule, method, func):
                result = self.module.main()
            return result

        with patch.object(builtins, 'open', open_file):
            if failed:
                return run('fail_json', fail_json)
            else:
                return run('exit_json', exit_json)

    def test_simple_jail(self):
        set_module_args({
            'name': 'example',
            'state': 'present',
        })
        result = self.execute_module()
