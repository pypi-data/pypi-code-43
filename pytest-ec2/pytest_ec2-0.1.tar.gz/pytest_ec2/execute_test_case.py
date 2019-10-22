import subprocess
from configparser import ConfigParser


def get_config():
    parser = ConfigParser()
    parser.read('pytest.config')
    return parser


if __name__ == '__main__':
    config = get_config()
    update_config = False
    if config.has_option('pytest_config', 'backend_path') is False:
        config.set(
            'pytest_config',
            'backend_path',
            input('Please specify the path of your backend code: '),
        )
        update_config = True
    if config.has_option('pytest_config', 'ec2_pem_key_path') is False:
        config.set(
            'pytest_config',
            'ec2_pem_key_path',
            input('Please specify the path of your EC2 .pem key: ')
        )
        update_config = True
    if update_config:
        configfile = open("pytest.config", 'w')
        config.write(configfile)
        configfile.close()

    branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE)
    branch = branch.stdout.decode("utf-8").strip('\n')
    branch = input('Please enter the test case branch(default is {}): '.format(branch)) or branch
    Process = subprocess.call('./pytest.sh %s %s %s' % (
        branch,
        config.get('pytest_config', 'backend_path'),
        config.get('pytest_config', 'ec2_pem_key_path'),
    ), shell=True)