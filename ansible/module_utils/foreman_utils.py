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


def elements_from_name(resource, name, module, foreman_client):
    indexed_resource = ['hosts', 'locations', 'hostgroups', 'ptables',
                        'domains', 'subnets', 'computeprofiles',
                        'computeresources']
    unindexed_resource = ['organizations']
    results = []
    try:
        if resource in indexed_resource:
            index = 'index_' + resource
            search = 'name=' + '"' + name + '"'
            results = getattr(foreman_client, index)(search=search)['results']
        elif resource in unindexed_resource:
            search = 'search=name=' + '"' + name + '"'
            results = foreman_client.do_get('/api/' + resource,
                                            search)['results']

    except Exception as e:
        msg = 'Error getting ' + name + ' in ' + resource + ': ' + e.message
        module.fail_json(msg=msg)
    if len(results) > 0:
        return results
    else:
        return None


def single_element_from_name(resource, name, module, foreman_client):
    elements = elements_from_name(resource, name, module, foreman_client)
    if elements is None:
        element = None
    elif len(elements) == 1:
        element = elements[0]
    else:
        msg = 'More that one item was found for ' + name + ' in ' + resource
        raise ForemanMoreThanExpectedElements(msg)
    return element


def id_from_name(resource, name, module, foreman_client):
    element = single_element_from_name(resource, name, module, foreman_client)
    if element is None:
        raise ForemanNotFoundElement('No element ' + name + ' in ' + resource)
    else:
        return element['id']

def subnet_from_network(network, module, foreman_client):
    results = []
    try:
        index = 'index_subnets'
        search = 'network=' + '"' + network + '"'
        results = getattr(foreman_client, index)(search=search)['results']
    except Exception as e:
        msg = 'Error getting ' + network + ' in networks: ' + e.message
        module.fail_json(msg=msg)
    if len(results) > 0:
        return results[0]['id']
    else:
        raise ForemanNotFoundElement("Network " + network + " not found")


class ForemanNotFoundElement(Exception):
    pass


class ForemanMoreThanExpectedElements(Exception):
    pass
