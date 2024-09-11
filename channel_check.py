import os
import sys
import yaml

outlawed_channels = [
    'defaults',
]


def check_file(filename):
    """Load YAML file and check for outlawed channels under top-level 'channels' key"""
    reject = False
    try:
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading '{filename}': {e}")
        return reject

    if data:
        if 'channels' in data:
            for channel in data['channels']:
                if channel in outlawed_channels:
                    print(f"Channel '{channel}' is not allowed in '{filename}'")
                    reject = True
    return reject


def check_files(filenames):
    """Check multiple files"""
    reject = False
    for filename in filenames:
        reject |= check_file(filename)
    return reject


def recurse_folders(folder):
    """Recursively find all YAML files"""
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.yml') or file.endswith('.yaml'):
                yield os.path.join(root, file)


if __name__ == '__main__':
    print("Checking for outlawed channels")
    if len(sys.argv) < 2:
        print("Usage: channel_check.py <folder>")
        sys.exit(1)
    folder = sys.argv[1]
    reject = check_files(recurse_folders(folder))
    if reject:
        sys.exit(1)
