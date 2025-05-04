#!/usr/bin/python3
import json
import sys
from ansible_collections.community.vmware.plugins.module_utils.vmware import connect_to_api, get_all_objs
from ansible.module_utils.basic import AnsibleModule

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
