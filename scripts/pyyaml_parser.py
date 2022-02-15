#!/usr/bin/python3

# This script will read a values-secret.yaml file in the user's home directory and output lines suitable to feed
# to vault to load them as secrets.

import yaml
import pathlib

homedir = pathlib.Path.home()
secretfile = pathlib.Path.joinpath(homedir, "values-secret.yaml")

with open(secretfile) as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

    for k in data['secrets']:
        values = ''
        for (name, value) in data['secrets'][k].items():
            values += f' {name}="{value}" '

        print(f'vault kv put secret/hub/{k} {values}')
        values = ''
