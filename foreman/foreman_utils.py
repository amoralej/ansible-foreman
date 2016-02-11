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

def get_multiple_elements_from_name(resource,name,module,foreman_client):
    indexed_resource=['hosts','locations','hostgroups','ptables','domains','subnets', 'computeprofiles', 'computeresources']
    unindexed_resource=['organizations']
    results=[]
    try:
        if resource in indexed_resource:
            results=getattr(foreman_client,'index_' + resource)(search='name=' + '"' + name +'"')['results']
        elif resource in unindexed_resource:
            results=foreman_client.do_get('/api/' + resource, 'search=name=' + '"' + name +'"')['results']
    except Exception as e:
        module.fail_json(msg='Error getting element ' + name + ' in resource ' + resource + ': ' + e.message)
    if len(results)>0:
        return results
    else:
        return None

def get_single_element_from_name(resource,name,module,foreman_client):
    elements=get_multiple_elements_from_name(resource,name,module,foreman_client) 
    if elements is None:
        element=None
    elif len(elements) == 1:
        element=elements[0]
    else:
        raise ForemanMoreThanExpectedElements('More that one item was found for ' + name + ' in ' + resource)
    return element

def get_single_id_from_name(resource,name,module,foreman_client):
    element=get_single_element_from_name(resource,name,module,foreman_client) 
    if element is None:
        raise ForemanNotFoundElement('No element ' + name + ' found in ' + resource)
    else:
        return element['id']

class ForemanNotFoundElement(Exception):
    pass

class ForemanMoreThanExpectedElements(Exception):
    pass
