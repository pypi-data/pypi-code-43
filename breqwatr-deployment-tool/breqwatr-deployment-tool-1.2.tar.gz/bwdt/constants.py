""" BWDT Constants """

# S3 Configs
S3_BUCKET = 'breqwatr-deployment-tool'
APT_TARGZ_KEY = 'apt.tar.gz'
BWDT_TARGZ_KEY = 'bwdt.tar.gz'
CLOUDYML_KEY = 'cloud.yml'

# Current latest tag
TAG = '7.0'

# Images used for breqwatr deployment & mgmt
SERVICE_IMAGE_TAGS = {
    'registry': '2',
    'breqwatr/ansible': TAG,
    'breqwatr/arcus-api': TAG,
    'breqwatr/arcus-client': TAG,
    'breqwatr/arcus-mgr': TAG,
    'breqwatr/apt': TAG,
    'breqwatr/pip': TAG,
    'breqwatr/pxe': TAG
}

# Images to pull when syncing the registry
KOLLA_IMAGE_TAGS = {
    'kolla/ubuntu-source-neutron-server': TAG,
    'kolla/ubuntu-source-neutron-openvswitch-agent': TAG,
    'kolla/ubuntu-source-neutron-dhcp-agent': TAG,
    'kolla/ubuntu-source-neutron-l3-agent': TAG,
    'kolla/ubuntu-source-neutron-metadata-agent': TAG,
    'kolla/ubuntu-source-heat-api': TAG,
    'kolla/ubuntu-source-heat-engine': TAG,
    'kolla/ubuntu-source-heat-api-cfn': TAG,
    'kolla/ubuntu-source-nova-compute': TAG,
    'kolla/ubuntu-source-nova-novncproxy': TAG,
    'kolla/ubuntu-source-nova-ssh': TAG,
    'kolla/ubuntu-source-nova-placement-api': TAG,
    'kolla/ubuntu-source-nova-api': TAG,
    'kolla/ubuntu-source-nova-consoleauth': TAG,
    'kolla/ubuntu-source-nova-conductor': TAG,
    'kolla/ubuntu-source-keystone-ssh': TAG,
    'kolla/ubuntu-source-nova-scheduler': TAG,
    'kolla/ubuntu-source-keystone': TAG,
    'kolla/ubuntu-source-keystone-fernet': TAG,
    'kolla/ubuntu-source-cinder-volume': TAG,
    'kolla/ubuntu-source-cinder-api': TAG,
    'kolla/ubuntu-source-cinder-scheduler': TAG,
    'kolla/ubuntu-source-glance-api': TAG,
    'kolla/ubuntu-source-openvswitch-db-server': TAG,
    'kolla/ubuntu-source-openvswitch-vswitchd': TAG,
    'kolla/ubuntu-source-kolla-toolbox': TAG,
    'kolla/ubuntu-source-fluentd': TAG,
    'kolla/ubuntu-source-memcached': TAG,
    'kolla/ubuntu-source-multipathd': TAG,
    'kolla/ubuntu-source-nova-libvirt': TAG,
    'kolla/ubuntu-source-keepalived': TAG,
    'kolla/ubuntu-source-chrony': TAG,
    'kolla/ubuntu-source-mariadb': TAG,
    'kolla/ubuntu-source-haproxy': TAG,
    'kolla/ubuntu-source-iscsid': TAG,
    'kolla/ubuntu-source-rabbitmq': TAG,
    'kolla/ubuntu-source-cron': TAG,
    'kolla/ubuntu-source-tgtd': TAG
}
