import os

# redshift cluster
rs_pwd = os.environ.setdefault('redshift_pwd', '****')
rs_dsn = os.environ.setdefault('redshift_dsn', '****')
rs_usr = os.environ.setdefault('redshift_usr', 'dataplatform')
