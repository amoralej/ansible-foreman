## Ansible module to manage foreman hosts

### Installation 

Copy the content of ansible directory in your ansible installation:

```
cp -pr ansible "$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")"
```

### Using it

Three different modules have been created:

- foreman_host: to create/delete host in foreman
- foreman_host_facts: to retrieve fact about foreman host
- foreman_host_power: to power on/off/reset hosts in foreman which support power management

Options of each module are docummented using ansible-doc, try ansible-doc <module name>

### TODO

- Update params and hostgroup (as workaround, host can be deleted / created)
- Change strings concatenation to printf format

