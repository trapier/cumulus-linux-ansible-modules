#!/usr/bin/env python
#
# Copyright (C) 2014, Cumulus Networks www.cumulusnetworks.com
#
#
DOCUMENTATION = '''
---
module: cl_interface
author: Stanley Karunditu
short_description: Configures a front panel , bridge or bond interface.
description:
    - Configures a front panel, management, loopback, bridge or bond interface.
options:
    name:
        description:
            - name of the interface
        required: true
    ipv4:
        description:
            - list of IPv4 addresses to configure on the interface. use CIDR
            syntax.
    ipv6:
        description:
            - list of IPv6 addresses  to configure on the interface. use CIDR
            syntax
    bridgemems:
        description:
            - list ports associated with the bridge interface.

    bondmems:
        description:
            - list ports associated with the bond interface
notes:
    - Cumulus Linux Interface Documentation - http://cumulusnetworks.com/docs/2.0/user-guide/layer_1_2/interfaces.html
    - Contact Cumulus Networks @ http://cumulusnetworks.com/contact/
'''
EXAMPLES = '''
#Example playbook entries using the cl_interface

## configure a front panel port with an IP
cl_interface: name=swp1  ipv4=10.1.1.1/24

## configure a front panel port with multiple IPs
cl_interface: name=swp1 ipv4=['10.1.1.1/24', '20.1.1.1/24']

## configure a bridge interface with a few trunk members and access port
cl_interface: name=br0  bridgemems=['swp1-10.100', 'swp11']

## configure a bond interface with an IP address
cl_interface: name=br0 bondmems=['swp1', 'swp2'] ipv4='10.1.1.1/24'
'''


def get_iface_type(module):
    if module.params.get('bridgemems'):
        return 'bridge'
    elif module.params.get('bondmems'):
        return 'bond'
    elif module.params.get('name') == 'lo':
        return 'loopback'
    elif re.match('^eth', module.params.get('name')):
        return 'mgmt'
    elif re.match('^swp', module.params.get('name')):
        return 'swp'
    else:
        _name = module.params.get('name')
        _msg = 'unable to determine interface type %s' % (_name)
        module.fail_json(msg=_msg)


def add_ipv4(module, iface):
    addrs = module.params.get('ipv4')
    if not 'config' in iface:
        iface['config'] = {}
    if not 'address' in iface['config']:
        iface['config']['address'] = None
    iface['config']['address'] = addrs


def sortdict(od):
    res = {}
    for k, v in sorted(od.items()):
        if isinstance(v, dict):
            res[k] = sortdict(v)
        elif isinstance(v, list):
            res[k] = sorted(v)
        else:
            res[k] = v
    return res

def config_lo_iface(module, iface):
    add_ipv4(module, iface)
#    add_ipv6(module, iface)
#    generate_config(iface)

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, type='str'),
            bridgemems=dict(type='str'),
            bondmems=dict(type='str'),
            ipv4=dict(type='str'),
            ipv6=dict(type='str')
        ),
        mutually_exclusive=[
            ['bridgemems', 'bondmems']
        ]
    )

    _ifacetype = get_iface_type(module)
    iface = { ifacetype: _ifacetype }
    if ifacetype == 'lo':
        config_lo_iface(module, iface)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()