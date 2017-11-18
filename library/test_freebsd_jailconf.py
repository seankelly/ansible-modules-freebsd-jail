
import json

from ansible.compat.tests import unittest
from ansible.compat.tests.mock import mock_open, patch
from ansible.module_utils import basic
from ansible.module_utils.six.moves import builtins
from ansible.module_utils._text import to_bytes

import freebsd_jailconf


class AnsibleExitJson(Exception):
    pass


class AnsibleFailJson(Exception):
    pass


def exit_json(*args, **kwargs):
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


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

    def execute_module(self, failed=False, changed=False, jail_contents=b''):
        mocked_open = mock_open(read_data=jail_contents)
        with patch.object(builtins, 'open', mocked_open):
            if failed:
                return self.failed(), mocked_open
            else:
                return self.changed(changed), mocked_open

    def changed(self, changed=False):
        with patch.object(basic.AnsibleModule, 'exit_json', exit_json):
            with self.assertRaises(AnsibleExitJson) as exc:
                self.module.main()
        result = exc.exception.args[0]
        self.assertEqual(result['changed'], changed, result)
        return result

    def failed(self):
        with patch.object(basic.AnsibleModule, 'fail_json', fail_json):
            with self.assertRaises(AnsibleFailJson) as exc:
                self.module.main()
        result = exc.exception.args[0]
        self.assertTrue(result['failed'], result)
        return result

    def test_simple_jail(self):
        set_module_args({
            'name': 'example',
            'state': 'present',
        })
        result, mocked_open = self.execute_module()
