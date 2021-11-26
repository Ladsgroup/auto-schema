import json

import requests


def get_replicas(dc, section):
    section_in_config = 'DEFAULT' if section == 's3' else section
    og_config = requests.get(
        'https://noc.wikimedia.org/dbconfig/{}.json'.format(dc)).json()
    with open('og_config.json', 'w') as f:
        f.write(json.dumps(og_config))
    type_in_config = 'sectionLoads' if section.startswith(
        's') else 'externalLoads'
    return og_config[type_in_config][section_in_config][1]
