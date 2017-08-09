#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, json, socket, datetime
from dopy.manager import DoManager
from key_reader import get_key
from collections import defaultdict
from rsa_key_handler import get_rsa_key


def _pretty_print(o):
    if isinstance(o, str):
        print(o)
    else: 
        print(str(json.dumps(o, indent=4)).replace('\\n', '\n        '))

def _do_creator():
    return DoManager(None, get_key(), api_version=2)

def destroy_droplet(*args):
    """
    Destroys a droplet
    Usage:
        id
    Arguments:
        id: id of the droplet to destroy
    """
    droplet_id = int(args[0])
    do = _do_creator()
    _pretty_print(do.destroy_droplet(droplet_id))

def create_small_droplet(*args):
    """
    Creates a new droplet

    Usage:
        name region image
    Parameters:
        name: the name of the droplet
        region: the region the droplet should be put in; a list
                of the possible regions can be found in `regions`.
                Accepts either a name (in which case it gets the first possible match) or the slug id
        image: the image id to be used; can be found in `images`
    """
    name = args[0]
    region = next(reg for reg in _get_regions([args[1]]))
    region_id = region['id']
    image = args[2]
    size = '512mb' if '512mb' in region['sizes'] else next(region['sizes'])
    _pretty_print("Creating image with name {name}, region {region}, image {image} and size {size}".format(name=name, region=region_id, image=image, size=size))
    ssh_add()
    ssh_id = _get_key_id()
    do = _do_creator()
    _pretty_print(do.new_droplet(name=name, size_id=size, image_id=image, region_id=region_id, ssh_key_ids=[ssh_id]))
    

def _get_regions(names):
    regions = _do_creator().all_regions()
    useful_regions = None
    if names and len(names) == 1:
        direct_match = next((region for region in regions if names[0].lower() in region['slug'].lower()), None)
        if not direct_match is None:
            useful_regions = [direct_match]
    if not useful_regions:
        useful_regions = [region for region in regions if not names or any(search in region['name'].lower() for search in names)]
    model = [{'name': region['name'], 'sizes': region['sizes'], 'id': region['slug']} for region in useful_regions]
    return model

def list_images(*args):
    """
    List available images
    Usage:
        [name] ...
    Arguments:
        name: (optional, multiple) if given, lists only images whose names have at least on of the given ones as substring
    """
    images = _do_creator().all_images()
    _pretty_print([{'id': image['slug'], 'name': image['name']} for image in images if not args or any(((not image['slug'] is None) and search.lower() in image['slug'].lower()) or ((not image['name'] is None) and search.lower() in image['name'].lower()) for search in args)])

def list_regions(*args):
    """
    List available regions

    Usage:
        [name] ...

    Parameters:
        name: (optional, multiple) if given, lists only regions whose name have at least one of the given ones as substrings
    """
    _pretty_print(_get_regions(args))

def list_droplets_verbose(*args):
    """
    Lists all active droplets with all information
    """
    _pretty_print(_do_creator().all_active_droplets())

def list_droplets(*args):
    _pretty_print([
        { 'id': droplet['id'], 'name': droplet['name']}
        for droplet in 
        _do_creator().all_active_droplets()
        ])

def _inverted_mappings(original_mappings):
    inverted = defaultdict(list)
    for (key, value) in original_mappings.items():
        inverted[value].append(key)
    return inverted

def print_command_list(*args):
    """
    Prints a list of possible actions
    """
    _pretty_print("\n".join(", ".join(actions) for actions in _inverted_mappings(_ACTION_MAPPING).values()))

def print_help(*args):
    """
    Prints help

    Usage:
        [command] ...

    Arguments:
        command: (optional, multiple) if any command is given, show only help relative to them
    """
    inverted = _inverted_mappings(_ACTION_MAPPING)

    data = \
    [
        {
            'names': value,
            'action description': key.__doc__.strip()
        }
        for (key, value) in inverted.items()
        if not args or any(action_names in args for action_names in value)
    ]
    _pretty_print(data)

def ssh_add(*args):
    """
    If the current public key isn't on DO, adds it

    Usage:
        [name] [path]

    Arguments:
        name: (optional) name to give to the key; default: AUT_$hostname_$date
        path: (optional) path of the public key
    """
    name = "AUT_{hostname}_{date}".format(hostname=socket.gethostname(), date=datetime.date.today().isoformat())
    path = None
    try:
        name = args[0]
        path = args[1]
    except:
        pass
    if _check_key(path):
        _pretty_print("Key already present")
    else:
        _pretty_print("Adding key {name}...".format(name=name))
        local_key = _get_rsa_key_path(path)
        do = _do_creator()
        do.new_ssh_key(name, local_key)

def _get_rsa_key_path(path):
    key = get_rsa_key() if path is None else get_rsa_key(path)
    return key

def _check_key(path:str=None) -> bool:
    return not _get_key_id(path) is None

def _get_key_id(path:str=None) -> int:
    local_key = _get_rsa_key_path(path)
    do = _do_creator()
    for remote_key in do.all_ssh_keys():
        if remote_key['public_key'].strip() == local_key.strip():
            return remote_key['id']
    return None


def ssh_check(*args):
    """
    Checks if the ssh key from the current pc is loaded on DO

    Usage:
        [path]

    Arguments:
        path: (optional) path of the public key
    """
    path = None
    try:
        path = args[0]
    except:
        pass
    key_id = _get_key_id(path)
    if key_id:
        _pretty_print("Key present, id: {id}".format(id=key_id))
    else:
        _pretty_print("No key found")

def ssh_list(*args):
    """
    List the names of the currently loaded ssh keys
    """
    do = _do_creator()
    _pretty_print([{ 'name': key['name'], 'id': key['id'] } for key in do.all_ssh_keys()]) 

def ssh_remove(*args):
    """
    Removes an ssh key

    Usage:
        [key_id]
    Arguments:
        key_id: (optional) the id of the key to remove; default: current one, if existing
    """
    try:
        key_id = int(args[0])
    except:
        key_id = _get_key_id()


    do = _do_creator()
    try:
        do.destroy_ssh_key(key_id)
        _pretty_print("Destroyed key {id}".format(id=key_id))
    except:
        _pretty_print("Key {id} couldn't be destroyed".format(id=key_id))


_ACTION_MAPPING = {
        'droplets': list_droplets,
        'list_droplets' : list_droplets,
        'droplets_verbose': list_droplets_verbose,
        'create': create_small_droplet,
        'destroy': destroy_droplet,

        'regions': list_regions,
        'images': list_images,

        'help': print_help,
        'print_help': print_help,

        'commands': print_command_list,

        'ssh_check': ssh_check,
        'ssh_add': ssh_add,
        'ssh_list': ssh_list,
        'ssh_remove': ssh_remove,
}

def main():
    args = sys.argv[1:]
    if not args:
        print_command_list()
    else:
        action = args[0] 
        _ACTION_MAPPING[action](*(args[1:]))

if __name__ == "__main__":
    main()
