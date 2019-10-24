from asset_inventory import AssetManager

import json

from pathlib import Path

username = 'muhannad'
psssword = '123321'
ssh_key = '/Users/muhannad/.ssh/ansible'
hosts = ['192.168.56.101']

tests_path = Path(__file__).parent.absolute()
resutls_path = tests_path / 'results'
resutls_path.mkdir(exist_ok=True)


def main():
    asset_manager = AssetManager(remote_user=username, password=psssword, ssh_key=ssh_key, connection='paramiko')
    asset_manager.fetch(hosts=hosts)
    for result in asset_manager.results():
        if result.status is 'success':
            data_path = resutls_path / f'{result.host}_data.json'
            facts_path = resutls_path / f'{result.host}_facts.json'
            open(file=data_path, mode='w+').write(json.dumps(result.data, indent=2))
            open(file=facts_path, mode='w+').write(json.dumps(result.facts, indent=2))


if __name__ == "__main__":
    main()
