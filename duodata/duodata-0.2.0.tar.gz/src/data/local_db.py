from sqlalchemy import create_engine
from duodata.settings import duodata_data_dir

local_db = create_engine('sqlite:///%s/duodata_data.db' % duodata_data_dir)
