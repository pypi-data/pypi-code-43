from flutter_debugger import *
import os
import time

logger = create_logger()


def package_flutter_assets() -> (bool, str):
    begin_time = time.time()

    project_name = 'test_project'
    archive_folder = 'debug_archives'

    # 运行flutter的打包代码
    if not check_shcommand_exist("flutter"):
        logger.error("Flutter命令不存在，无法打包")
        return False, "Flutter命令不存在，无法打包", ""
    else:
        logger.info("准备打包Flutter项目")
    run_command("flutter build bundle --debug")

    # 将flutter的打包产物压缩成zip包
    archive_dir = os.path.abspath(archive_folder)
    archive_file_name = project_name + '_debug'
    if not os.path.exists(archive_dir):
        os.mkdir(archive_dir)
    flutter_assets_dirs = [os.path.abspath('./build/flutter_assets'),
                           os.path.abspath('./ios/Flutter/App.framework/flutter_assets'),
                           os.path.abspath('./.ios/Flutter/App.framework/flutter_assets')]

    flutter_assets_archive_path = os.path.abspath('./' + archive_folder + '/' + archive_file_name + '.zip')
    have_avaliable_flutter_dir = False
    for flutter_assets_dir in flutter_assets_dirs:
        if os.path.exists(flutter_assets_dir):
            have_avaliable_flutter_dir = True
            logger.info("开始归档flutter_assets目录")
            logger.info("flutter_assets目录位置：{0}".format(flutter_assets_dir))
            archive_file_path = archive(flutter_assets_dir, flutter_assets_archive_path)
            logger.info(str.format("归档flutter_assets目录结束，路径：{0}", archive_file_path))
            break

    if not have_avaliable_flutter_dir:
        logger.error("打包Flutter项目失败，不存在可用的flutter_assets目录")
        return False, "打包Flutter项目失败，不存在可用的flutter_assets目录", ""

    end_time = time.time()
    cost_time = end_time - begin_time
    logger.info("打包耗时: {0}s".format(cost_time))

    return True, archive_file_name, archive_file_path

