#!/usr/bin/env python3

from os import system, path
import os, subprocess, re, json, pprint, argparse, shlex



vm_name = 'hero'
# vm_name = 'jubu'
vm_folder = '/data/virtualbox/vms'
vm_storage_folder = '/data/virtualbox/disks'
vm_size = 48000
ostype = 'Ubuntu_64' #find types using 'VBoxManage list ostypes'

def execute(cmd):
    try:
        cmd = shlex.split(cmd)
        byte_output = subprocess.check_output(cmd)
        output = byte_output.decode('UTF-8')
        return output
    except subprocess.CalledProcessError as cpe:
        return None
    except Exception as ex:
        print(ex)
        return None

def storagectl_create(vm_name, controller_type):
    if controller_type.lower() == 'sata':
        cmd = f'VBoxManage storagectl {vm_name} --name "SATA Controller" --add sata --controller IntelAhci'
    elif controller_type.lower() == 'ide':
        cmd = f'VBoxManage storagectl {vm_name} --name "IDE Controller" --add ide --controller PIIX4'
    else:
        return None
    
    output = execute(cmd)

def storageattach(vm_name, controller_type, disk_path):
    if 'sata' == controller_type.lower():
        medium_type = 'hdd'
    elif 'ide' == controller_type.lower():
        medium_type = 'dvddrive'

    cmd = f'VBoxManage storageattach {vm_name} --storagectl "{controller_type.upper()} Controller" --port 0 --device 0 --type {medium_type} --medium {disk_path}'
    try:
        output = execute (cmd)
        return output
    except Exception:
        return None

def vm_create(vm_name, ostype, vb_folder, disk_size_mb):
    vms_folder = os.path.join(vb_folder, 'vms')
    disks_folder = os.path.join(vb_folder, 'vdisks')
    diskname = vm_name + '.vdi'
    disk_path = os.path.join(disks_folder, diskname)
    
    cmd = f"VBoxManage createvm --name {vm_name} --ostype {ostype} --register --basefolder {vms_folder}"
    result = vm_create_output = execute(cmd)
    if not result:
        return
    
    cmd = f'VBoxManage modifyvm {vm_name} --ioapic on'
    output = execute(cmd)
    cmd = f'VBoxManage modifyvm {vm_name} --memory 8192 --vram 128'
    output = execute(cmd)
    cmd = f'VBoxManage modifyvm {vm_name} --nic1 nat'
    output = execute(cmd)

    disk_create_output = disk_create(disk_path, disk_size_mb)
    if not disk_create_output:
        return None
    controller_type = "SATA"
    storagectl_output = storagectl_create(vm_name, controller_type)
    attach_output = storageattach(vm_name,controller_type, disk_path)
    print(attach_output)

    controller_type = "IDE"
    output = execute(cmd)
    iso_disk_path = '/data/isos/ubuntu-21.04-live-server-amd64.iso'
    storagectl_output = storagectl_create(vm_name, controller_type)
    attach_output = storageattach(vm_name,controller_type, iso_disk_path)
    print(attach_output)

    cmd = f'VBoxManage modifyvm {vm_name} --boot1 dvd --boot2 disk --boot3 none --boot4 none'
    output = execute(cmd)

    #Enable RDP
    cmd = f'VBoxManage modifyvm {vm_name} --vrde on'
    output = execute(cmd)
    cmd = f'VBoxManage modifyvm {vm_name} --vrdemulticon on --vrdeport 10001'
    output = execute(cmd)

def vm_remove_attached_disks(vm_name):
    disks = attached_disks_UUIDs(vm_name)
    if not disks:
        return None
    uuids=[]
    hdd_keys=[]
    pattern = r'(.*?)\(UUID:\s*(.+)\)$'
    for k,v in disks.items():
        match = re.match(pattern, v)
        if match:
            uuids.append(match.groups()[1])
            hdd_keys.append(k)
    
    for k in hdd_keys:
        cmd = f'VBoxManage storageattach {vm_name} --storagectl "SATA Controller" --port 0 --device 0 --medium  none'
        print(cmd)
        output = execute(cmd)
        print(output)

    return uuids

def vm_delete(vm_name, delete_disk):
    vm_remove_attached_disks(vm_name)
    cmd = f'VBoxManage unregistervm --delete {vm_name}'
    output = execute(cmd)

    if delete_disk:
        output = disk_delete(vm_name)

    return output

def filter_dict(d, f):
    ''' Filters dictionary d by function f. '''
    newDict = dict()

    # Iterate over all (k,v) pairs in names
    for key, value in d.items():

        # Is condition satisfied?
        if f(key, value):
            newDict[key] = value

    return newDict

def vm_vminfo(vm_name):
    cmd = f"VBoxManage showvminfo {vm_name}"
    vminfo_string = execute(cmd)
    if not vminfo_string:
        return None
    else:
        result = string_to_dictionary(vminfo_string)
        return result

def attached_disks_UUIDs(vm_name):
    vminfo = vm_vminfo(vm_name)
    if not vminfo:
        return None
    result = filter_dict(vminfo, lambda k,v: k.startswith('SATA')  or k.startswith('IDE'))
    return result
    



def disk_create(disk_path, size):
    if not disk_path.endswith('.vdi'):
        disk_path += '.vdi'
    
    if path.isfile(disk_path):
        return None

    cmd = f"VBoxManage createmedium disk --filename {disk_path} --size {size}"
    output = execute(cmd)
    return disk_path



def vm_list():
    cmd = f'vboxmanage list vms'
    byte_output = subprocess.check_output(cmd.split())
    output= byte_output.decode('UTF-8')
    return output

def vb_disk_delete(disk_uuid):
    cmd = f'vboxmanage closemedium disk {disk_uuid} --delete'
    system(cmd)

def disk_list():
    cmd = f'vboxmanage list hdds'
    byte_output = subprocess.check_output(cmd.split())
    output = byte_output.decode('UTF-8').rstrip()
    return output

# def disk_delete_by_uuid(uuids):
#     for uuid in uuids:
#         cmd = 

def disk_delete(disk_path):
    disks = disk_dictionary()
    
    for key, disk in disks.items():
        if disk['Location'] == disk_path:
            vb_disk_delete(disk['UUID'])
            if os.path.isfile(disk_path):
                os.remove(disk_path)
            return

def string_to_dictionary(input):
    lines = input.split('\n')
    pattern = r'^(.*?):\s*(.*?)$'
    settings = {}
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            key = match.groups()[0]
            value  = match.groups()[1]
            settings[key] = value
    return settings

def disk_dictionary():
    input = disk_list()
    lines = input.split('\n')
    pattern = r'^(.*?):\s*(.*?)$'

    disks = {}
    disk = {}
    for line in lines:
        match = re.match(pattern, line)
        if match:
            # print(f"key: {match.groups()[0]}, value: {match.groups()[1]}")
            
            key = match.groups()[0]
            value  = match.groups()[1]
            if key == 'UUID':
                disk_key = value
            
            disk[key] = value
            if key == 'Capacity':
                value = int(value.split()[0])
                disk[key] = value
                
            if key == 'Location':
                disk_path = os.path.splitext(os.path.basename(value))[0]
                disk_name = os.path.basename(disk_path)
                disk['name']=disk_path
                disks[disk_name] = disk
                disk_key = value

            if key == 'Encryption':
                # print(disk)
                disks[disk_key] = disk
                disk = {}
    return disks

def main():
    parser = argparse.ArgumentParser(description="Create VirtualBox VM")
    parser.add_argument('--name','-n', default=vm_name)
    parser.add_argument('--ostype', default='Ubuntu_64')
    parser.add_argument('--vb_folder', default='/data/jmurray/virtualboxvms')
    parser.add_argument('--size', default=vm_size, help="size of disk in MB")
    parser.add_argument('--vm_storagefolder', default='/data/jmurray/virtualboxvms/vmdisks')
    # parser.add_argument('--doctors', default=False, action="store_true", help='dump doctors')
    parser.add_argument('action', choices=['create', 'list', 'delete'], help='perform the specified action')

    args = parser.parse_args(['list'])
    # args = parser.parse_args(['--patients'])

    print(args)

    print(attached_disks_UUIDs(args.name))
    vm_delete(args.name, delete_disk=True)
    vm_create(args.name, args.ostype, args.vb_folder, args.size)

    # disk_create(vm_name, vm_size)
    # pprint.pprint(disk_dictionary())
    # pprint.pprint(vm_list())

if __name__ == "__main__":
    main()