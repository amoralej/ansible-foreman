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


from ansible.module_utils.basic import *
from ansible.modules.extras.foreman.foreman_utils import *

try:
    from foreman.client import Foreman 
    HAS_FOREMAN_CLIENT = True
except ImportError:
    HAS_FOREMAN_CLIENT = False


DOCUMENTATION = '''
---
module: foreman_host_fact
short_description: Add foreman_host and foreman_status facts for node
version_added: "2.0"
author: "Alfredo Moralejo (amoralej@redhat.com)"
description:
   - Add foreman_host and foreman_status facts for node
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
        - Name of the host in foreman
     required: true
requirements:
    - "python >= 2.7"
    - "python-foreman"
'''

EXAMPLES = '''
# Get foreman facts for server vm1.example.com
# 
- foreman_host_facts:
    url: https://mysat.example.com
    foreman_user: admin
    foreman_password: pass
    name: vm1.example.com
- debug:
    var: foreman_host

'''

def _get_host_status(module, foreman_client):
    id = get_single_id_from_name('hosts',module.params['name'],module,foreman_client)
    status = foreman_client.do_get("/api/hosts/" + str(id) + "/status","")
    return status

def main():

    argument_spec = dict(
        url                             = dict(required=True),
        foreman_user                    = dict(required=True),
        foreman_password                = dict(required=True, no_log=True),
        name                            = dict(required=True),
    )
    module = AnsibleModule(argument_spec)

    if not HAS_FOREMAN_CLIENT:
        module.fail_json(msg='python-foreman is required for this module')

    try:
        host_params = dict(module.params)
        foreman_client = Foreman(host_params['url'], (host_params['foreman_user'], host_params['foreman_password']), api_version=2)
        host=get_single_element_from_name('hosts',module.params['name'],module,foreman_client)
        status=_get_host_status(module, foreman_client)
        module.exit_json(changed=False, ansible_facts=dict(
            foreman_host=host, foreman_status=status))
    except Exception as e:
        module.fail_json(msg=e.message)


if __name__ == '__main__':
    main()
