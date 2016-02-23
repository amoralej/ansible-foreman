#!/usr/bin/python
# coding: utf-8 -*-
# Copyright (c) 2016 Red Hat
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.


try:
    from foreman.client import Foreman
    from retrying import retry
    HAS_REQS = True
except ImportError:
    HAS_REQS = False


DOCUMENTATION = '''
---
module: foreman_host_power
short_description: Applies a power action to a foreman host
version_added: "2.0"
author: "Alfredo Moralejo (amoralej)"
description:
   - Applies a power action to a foreman host
     This only can be applied to hosts that support power actions, as managed
     through compute resources or bare metal with IPMI configured in foreman
options:
   url:
     description:
        - URL of foreman (or satellite server)
     required: true
   foreman_user:
     description:
        -user to access foreman (or satellite server)
     required: true
   foreman_pass:
     description:
        -password to access foreman (or satellite server)
     required: true
   name:
     description:
        - Name that has to be given to the host
     required: true
   power_action:
     description:
        - The action to perform.
          Valid actions are (on/start), (off/stop), (soft/reboot),
          (cycle/reset)
     required: true
requirements:
    - "python >= 2.7"
    - "python-foreman"
    - "retrying"
'''

EXAMPLES = '''
# Reset a server
#
- foreman_host_power:
    state: present
    url: https://mysat.example.com
    foreman_user: admin
    foreman_password: pass
    power_action: reset
    name: vm1.example.com

'''


def _power_action(module, foreman_client):
        host_id = id_from_name('hosts', module.params['name'],
                               module, foreman_client)
        url = '/api/hosts/' + str(host_id) + '/power?power_action=' \
            + module.params['power_action']
        host = foreman_client.do_put(url, '')
        module.exit_json(changed='true', result='success')


def main():
    argument_spec = dict(
        url=dict(required=True),
        foreman_user=dict(required=True),
        foreman_password=dict(required=True, no_log=True),
        name=dict(required=True),
        power_action=dict(choices=['start', 'stop', 'poweroff', 'reboot',
                                   'reset', 'state', 'on', 'off', 'soft',
                                   'cycle'], required=True),
    )
    module = AnsibleModule(argument_spec)

    if not HAS_REQS:
        module.fail_json(msg='python-foreman and retrying required for module')

    try:
        host_params = dict(module.params)
        foreman_client = Foreman(host_params['url'],
                                 (host_params['foreman_user'],
                                 host_params['foreman_password']),
                                 api_version=2)
        power = _power_action(module, foreman_client)
    except Exception as e:
        module.fail_json(msg=e.message)

from ansible.module_utils.basic import *
from ansible.modules.extras.foreman.foreman_utils import *
if __name__ == '__main__':
    main()
