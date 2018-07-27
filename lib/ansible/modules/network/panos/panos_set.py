#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage PaloAltoNetworks Firewall
# (c) 2016, techbizdev <techbizdev@paloaltonetworks.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: panos_set
short_description: Execute arbitrary commands on a PAN-OS device using XPath and element
description:
    - Run an arbitrary `xapi` command taking an XPath (i.e get) or XPath and element (i.e set).
    - Runs a `set` command by default
    - This should support _all_ commands that your PAN-OS device accepts vi it's cli
    - `cli` commands are found as:
    - - Once logged in issue: `debug cli on`
      - Enter configuration mode by issuing: `configure`
      - Enter your set (or other) command, for example: `set deviceconfig system timezone Australia/Melbourne`
      - returns "<request cmd="set" obj="/config/devices/entry[@name='localhost.localdomain']/deviceconfig/system" cookie=XXXX><timezone>Australia/Melbourne</timezone></request>
      - The `xpath` is  "/config/devices/entry[@name='localhost.localdomain']/deviceconfig/system"
      - The `element` is "<timezone>Australia/Melbourne</timezone>"
author: "Jasper Aorangi (@spmp)"
version_added: "2.7"
requirements:
    - pan-python
options:
    command:
      xapi method name which supports `xpath` or `xpath` and `element`
    xpath:
      XPath of the configurable
    element (optional):
      Element of the configurable if required
extends_documentation_fragment: panos
'''

EXAMPLES = '''

- name: Set timezone on PA NVA
  panos_set:
    ip_address: "192.168.1.1"
    username: "my-random-admin"
    password: "admin1234"
    xpath: "/config/devices/entry/deviceconfig/system"
    element: "<timezone>Australia/Melbourne</timezone>"

- name: Commit configuration
  panos_commit:
    ip_address: "192.168.1.1"
    username: "my-random-admin"
    password: "admin1234"
'''

RETURN = '''
# Default return values
'''

ANSIBLE_METADATA = {'metadata_version': '0.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


from ansible.module_utils.basic import AnsibleModule

try:
  import pan.xapi
  HAS_LIB = True
except ImportError:
  HAS_LIB = False

def main():
  argument_spec = dict(
    ip_address  = dict(required = True),
    password    = dict(required = True, no_log=True),
    username    = dict(default  = 'admin'),
    command     = dict(default  = "set"),
    xpath       = dict(required = True),
    element     = dict(default  = None)
  )
  module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)
  if not HAS_LIB:
    module.fail_json(msg='pan-python is required for this module')

  ip_address    = module.params["ip_address"]
  password      = module.params["password"]
  username      = module.params['username']
  xpath         = module.params['xpath']
  element       = module.params['element']
  xcommand      = module.params['command']

  xapi = pan.xapi.PanXapi(
    hostname    = ip_address,
    api_username= username,
    api_password= password,
    timeout     = 60
  )
  
  if element == None:
  # Issue command with no `element`
    try:
        getattr(xapi, xcommand)(xpath=xpath)
    except Exception as e:
      raise Exception("Failed to run '{}' with xpath: '{}' with the following error: {}".format(
        xcommand, xpath, e))
  else:
  # Issue command with `element`
    try:
        getattr(xapi, xcommand)(xpath=xpath, element=element)
    except Exception as e:
      raise Exception("Failed to run '{}' with xpath: '{}' and element '{}' with the following error: {}".format(
        xcommand, xpath, element, e))

  module.exit_json(
    status      = "success"
  )


if __name__ == '__main__':
  main()
