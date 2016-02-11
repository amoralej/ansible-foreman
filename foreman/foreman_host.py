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
    HAS_REQS = True
except ImportError:
    HAS_REQS = False


DOCUMENTATION = '''
---
module: foreman_host
short_description: Create/Delete Hosts in foreman
version_added: "2.0"
author: "Alfredo Moralejo (amoralej@redhat.com)"
description:
   - Create or Remove hosts in foreman
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
   mac:
     description:
        - The Mac address of the host
     required: true
   organization_name:
     description:
        - The name of the organization assigned to the host
     required: true
   location_name:
     description:
        - The name of the location assigned to the host
     required: true
   hostgroup_name:
     description:
        - The name of the hostgroup assigned to the host
          Required unless state=absent
     required: False
   ip:
     description:
        - The ip address of the host.
     required: false
   build:
     description:
        - Set host in build mode
     default: false
   ptable_name:
     description:
        - The name of the partition table assigned to the host
     required: false
   state:
     description:
        - The desired status for the system, present or absent
     required: true
     default: present
   root_pass:
     description:
        - The password of root user applied in kickstarting
     required: false
   compute_resource:
     description:
        - The compute resource name used to deploy the host 
     required: false
   compute_profile:
     description:
        - The compute profile name used to deploy the host if deployng from
          compute resource
     required: false
   host_parameters_attributes:
     description:
        - List of parameters to set for host. It must be a list of dictionaries 
          with keys "name" and "value" (see examples)
     required: false
   interfaces_attributes:
     description:
        - List of additional interfaces configuration. It must be a list of  
          of dictionaries as defined in foreman API.
     required: false
requirements:
    - "python >= 2.7"
    - "python-foreman"
'''

EXAMPLES = '''
# Creates a new host vm1.example.com in foreman with some parameters, and provide ip address:
# 
- foreman_host:
    state: present
    url: https://mysat.example.com
    foreman_user: admin
    foreman_password: pass
    organization_name: myorg
    location_name: myloc
    name: vm1.example.com
    mac: 00:00:00:00:00:00
    ip: 192.168.100.3
    hostgroup_name: myhostgroup
    root_pass: "password"
    host_parameters_attributes: "[{'name': 'parameter', 'value': 'desired_value'}]"

# Create a new host vm1.example.com in foreman with a second NIC interface.
#
- foreman_host:
    state: present
    url: https://mysat.example.com
    foreman_user: admin
    foreman_password: pass
    organization_name: myorg
    location_name: myloc
    name: vm1.example.com
    mac: 00:00:00:00:00:00
    ip: 192.168.100.3
    hostgroup_name: myhostgroup
    root_pass: "password"
    interfaces_attributes: "[{'mac': '10:00:00:00:00:00', 'ip': '1.1.1.1', 'type': 'Nic::Managed' }]"
    
# Deletes a host vm1.example.com in foreman:
# 
- foreman_host:
    state: absent
    url: https://mysat.example.com
    foreman_user: admin
    foreman_password: pass
    organization_name: myorg
    location_name: myloc
    name: vm1.example.com

# Creates a host vm1.example.com in foreman using compute resources to create the system
# in a backend. IP will be assigned by foreman.

- foreman_host:
    state: absent
    url: https://mysat.example.com
    foreman_user: admin
    foreman_password: pass
    organization_name: myorg
    location_name: myloc
    name: vm1.example.com
    hostgroup_name=myhostgroup 
    build=true 
    compute_resource=RHEV_CLUSTER
    compute_profile=Big

'''

def _exit_hostvars(module, host, changed=True, result="success"):
    if host is None:
        hostvars={}
    else:
        hostvars={"name": module.params["name"],"id": host["id"], "ip": host["ip"]}
    module.exit_json(
        changed=changed, host=hostvars, result=result)


def _delete_host(module, foreman_client):
    element=get_single_element_from_name('hosts',module.params['name'],module,foreman_client)
    id=element["id"]
    ip=element["ip"]
    host={"name": module.params['name'], "id": id, "ip": ip }
    try:
        foreman_client.destroy_hosts(id)
    except Exception as e:
        module.fail_json(msg="Error in deleting host: %s" % e.message)
    _exit_hostvars(module, host, changed=True)


def _create_host(module, foreman_client):
    hostargs = {} 
    hostargs['name'] = module.params['name']
    hostargs['build'] = module.params['build']
    hostargs['organization_id'] = get_single_id_from_name("organizations",module.params['organization_name'],module,foreman_client)
    hostargs['location_id'] = get_single_id_from_name("locations",module.params['location_name'],module,foreman_client)

    if module.params['hostgroup_name']:
        hostargs['mac'] = module.params['mac']
 
    if module.params['hostgroup_name']:
        hostargs['hostgroup_id'] = get_single_id_from_name('hostgroups',module.params['hostgroup_name'],module,foreman_client)

    if module.params['compute_resource']:
        hostargs['compute_resource_id'] = get_single_id_from_name('computeresources',module.params['compute_resource'],module,foreman_client)

    if module.params['compute_profile']:
        hostargs['compute_profile_id'] = get_single_id_from_name('computeprofiles',module.params['compute_profile'],module,foreman_client)

    if module.params['root_pass']:
        hostargs['root_pass'] = module.params['root_pass']

    if module.params['ptable_name']:
        hostargs['ptable_id'] = get_single_id_from_name('ptables',module.params['ptable_name'],module,foreman_client)

    if module.params['ip']:
        hostargs['ip'] = module.params['ip']

    if module.params['interfaces_attributes']:
        hostargs['interfaces_attributes'] = eval(module.params['interfaces_attributes'])

    try:
        host = foreman_client.create_hosts(host=hostargs)
    except Exception as e:
        module.fail_json(msg="Error creating host: %s" % e.message )

    if module.params['host_parameters_attributes']:
        hostparams = {} 
        hostparams['host_parameters_attributes'] = eval(module.params['host_parameters_attributes'])
        try:
            host =foreman_client.update_hosts(host=hostparams, id=host['id']) 
        except Exception as e:
            module.fail_json(msg="Error creating host: %s" % e.message)
    _exit_hostvars(module, host)

def _get_host_state(module, foreman_client):
    state = module.params['state']
    host = get_single_element_from_name('hosts',module.params['name'],module,foreman_client)
    if host and state == 'present':
        _exit_hostvars(module, host, changed=False)
    if host and state == 'absent':
        return True
    if state == 'absent':
        _exit_hostvars(module, host=None, changed=False)
    return True


def main():

    argument_spec = dict(
        state                           = dict(default='present', choices=['absent', 'present']),
        url                             = dict(required=True),
        foreman_user                    = dict(required=True),
        foreman_password                = dict(required=True,no_log=True),
        build                           = dict(default='false', choices=['true', 'false']),
        name                            = dict(required=True),
        ip                              = dict(required=False),
        mac                             = dict(required=False),
        organization_name               = dict(required=True),
        location_name                   = dict(required=True),
        hostgroup_name                  = dict(required=False),
        ptable_name                     = dict(required=False),
        root_pass                       = dict(required=False),
        host_parameters_attributes      = dict(required=False),
        interfaces_attributes           = dict(required=False),
        compute_resource                = dict(required=False),
        compute_profile                 = dict(required=False),
    )
    module = AnsibleModule(argument_spec)

    if not HAS_REQS:
        module.fail_json(msg='python-foreman is required for this module')

    state = module.params['state']

    try:
        host_params = dict(module.params)
        foreman_client = Foreman(host_params['url'], (host_params['foreman_user'], host_params['foreman_password']), api_version=2)

        if state == 'present':
            _get_host_state(module, foreman_client)
            _create_host(module, foreman_client)
        elif state == 'absent':
            _get_host_state(module, foreman_client)
            _delete_host(module, foreman_client)
    except ValueError as e:
        module.fail_json(msg=e.message)

from ansible.module_utils.basic import *
from ansible.modules.extras.foreman.foreman_utils import *
if __name__ == '__main__':
    main()
