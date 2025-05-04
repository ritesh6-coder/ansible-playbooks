#!/usr/bin/python3
import json
import sys
import os

# Debugging: Print sys.path to see what Python is using
print("sys.path before modification:", sys.path)

# Add the collections path to sys.path (same path as in the container)
collections_path = '/var/lib/awx/.ansible/collections/ansible_collections'
if os.path.exists(collections_path):
    sys.path.append(collections_path)
    print(f"Added {collections_path} to sys.path")
else:
    print(f"Collections path {collections_path} does not exist")

print("sys.path after modification:", sys.path)

try:
    from ansible_collections.community.vmware.plugins.module_utils.vmware import connect_to_api, get_all_objs
except ImportError as e:
    print(f"Failed to import ansible_collections: {e}")
    sys.exit(1)

from ansible.module_utils.basic import AnsibleModule
from pyVim.connect import SmartConnect, Disconnect
import vim

def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            port=dict(type='int', default=443),
            validate_certs=dict(type='bool', default=False),
            vm_name=dict(type='str', required=True),
        )
    )

    try:
        # Connect to vSphere
        client = connect_to_api(module)
        # Get all VMs
        content = client.content
        vm_objs = get_all_objs(content, [vim.VirtualMachine])
        # Filter for the specified VM
        vm_info = []
        for vm in vm_objs:
            if vm.name == module.params['vm_name']:
                vm_info.append({
                    "guest_name": vm.name,
                    "power_state": vm.runtime.powerState,
                    "ip_address": vm.guest.ipAddress if vm.guest.ipAddress else "",
                    "uuid": vm.config.uuid,
                    "datacenter": vm.summary.runtime.host.parent.parent.name,
                    "folder": vm.parent.name,
                    "esxi_hostname": vm.runtime.host.name,
                    "guest_fullname": vm.config.guestFullName,
                })
        module.exit_json(changed=False, virtual_machines=vm_info)
    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()
