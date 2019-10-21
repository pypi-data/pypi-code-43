from glob import glob

try:
    import configparser as ConfigParser
except:
    import ConfigParser
import os.path


def get_config(config_info_file=None):
    """ Sample Use Case
    ============================================================================
    config_info_file="C:\\Users\\username\\project\\nbi_jv-nbijv\\notebooks\\upload_config.ini"
    data = get_config("your config file")
    files = data[0]   /* file path
    group_names = data[1]  /* ['Accelerator', 'Gyroscrop']
    group_columns = data[2]  /* ['3,4,5', '6,7,8']
    data_column_names = data[3]  /* ['accelx,accely,accelz', 'gyrox,gyroy,gyroz']
    metadata_columns = data[4]  /* [0,1]
    """
    if config_info_file is None:
        raise Exception(
            "*** Sorry, Config File Missing *** "
            + "file exist? "
            + str(os.path.isfile(config_info_file))
            + "..filename: "
            + config_info_file
        )

    config = ConfigParser.ConfigParser()
    config.read(config_info_file)
    sections = config.sections()
    if "File_Path" in sections[0]:
        filePath = config.get(sections[0], "path")
    else:
        print("Can not read config file...")

    # First try absolute path
    files = glob(filePath)
    if not files:
        # Then try relative to upload config file
        files = glob(os.path.join(os.path.split(config_info_file)[0], filePath))

    for i in range(len(files)):
        if os.path.splitext(files[i])[1] == ".h5":
            return [files, None, None, None, None]

    group_names = config.get(sections[1], "group_name")
    group_columns = config.get(sections[1], "group_column")
    data_column_names = config.get(sections[1], "data_column_name")
    metadata_columns = (
        (config.get(sections[2], "metadata_column")).split(",")
        if len(sections) > 2
        else None
    )
    groupnames = group_names.split("/")
    groupcolumns = group_columns.split("/")
    datacolumnnames = data_column_names.split("/")
    # metadatacolumns = metadata_columns.split(',')

    return [files, groupnames, groupcolumns, datacolumnnames, metadata_columns]
