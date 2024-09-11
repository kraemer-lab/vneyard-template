import os
import json
import gzip

FILENAME = os.environ.get('MANIFEST_FILENAME', 'manifest')
COMPRESSION = os.environ.get('MANIFEST_COMPRESSION', 'False').lower() == 'true'

reject_list = [
    '.snakemake',
    '.git',
    '.github',
]


def create_folder_structure_json(path):
    """Produces a folder hierarchy structure that mimics the github API format"""
    result = {
        'name': os.path.basename(path),
        'type': 'folder',
        'children': [],
    }

    # Check if the path is a directory
    if not os.path.isdir(path):
        return result

    # Iterate over the entries in the directory
    for entry in os.listdir(path):
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path) and entry not in reject_list:
            result['children'].append(create_folder_structure_json(entry_path))
        else:
            result['children'].append({'name': entry, 'type': 'file'})

    return result


folder_json = create_folder_structure_json('.')
folder_json_str = json.dumps(folder_json)

if COMPRESSION:
    with gzip.open(f'{FILENAME}.json.gz', 'wt', encoding='UTF-8') as zipfile:
        zipfile.write(folder_json_str)
else:
    with open(f'{FILENAME}.json', 'wt', encoding='UTF-8') as f:
        f.write(folder_json_str)
