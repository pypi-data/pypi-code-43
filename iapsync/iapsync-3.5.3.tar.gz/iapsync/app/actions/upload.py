import sys
import os
import signal
import time
import fcntl
import subprocess
from pathlib import Path
from iapsync.config import config
from iapsync.handlers import all_handlers
from iapsync.utils.transporter import transporter_path

def run(params, opts, data_to_upload):
    username = params['username']
    password = params['password']
    BUNDLE_ID = params['itc_conf']['BUNDLE_ID']
    output_dir = params['output_dir']
    APPSTORE_PACKAGE_NAME = params['APPSTORE_PACKAGE_NAME']
    tmp_dir = Path(output_dir + config.TMP_DIR).joinpath(BUNDLE_ID + '-' + params['target_env'])
    p = tmp_dir.joinpath(APPSTORE_PACKAGE_NAME)

    # 使用锁文件避免多个进程同时上传AppStore，iTMSTransporter会报错
    lock_file = params['lock_file']
    # 如果文件存在并不改写它，如果不存在则生成空文件
    try:
        open(lock_file, 'a').close()
    except Exception as e:
        raise e

    lock_file_handle = open(lock_file, 'r+')
    def acquire_upload_lock():
        print('Trying to acquire_upload_lock')
        begin_at = int(time.time())
        did_wait = False
        while True:
            fcntl.lockf(lock_file_handle, fcntl.LOCK_EX)
            try:
                lock_file_handle.seek(0)
                data = lock_file_handle.read()
                fcntl.lockf(lock_file_handle, fcntl.LOCK_UN)
                if data and data != config.INSTANCE_ID:
                    did_wait = True
                    time.sleep(1)
                    continue
            except Exception as e:
                fcntl.lockf(lock_file_handle, fcntl.LOCK_UN)
                print('acquire_upload_lock failed')
                raise e

            try:
                lock_file_handle.seek(0)
                lock_file_handle.write(config.INSTANCE_ID)
                lock_file_handle.truncate()
                print('Did acquire_upload_lock')
            except Exception as e:
                print('acquire_upload_lock failed')
                raise e
            finally:
                fcntl.lockf(lock_file_handle, fcntl.LOCK_UN)
            break
        end_at = int(time.time())
        if did_wait:
            print('Waited %d seconds acquiring upload lock' % (end_at - begin_at))

    def release_upload_lock():
        fcntl.lockf(lock_file_handle, fcntl.LOCK_EX)
        try:
            lock_file_handle.seek(0)
            lock_file_handle.truncate()
            print('Did release_upload_lock')
        except IOError as e:
            print('release_upload_lock failed')
            raise e
        finally:
            fcntl.lockf(lock_file_handle, fcntl.LOCK_UN)

    def sig_quit(_signum, _):
        fcntl.lockf(lock_file_handle, fcntl.LOCK_EX)
        try:
            lock_file_handle.seek(0)
            data = lock_file_handle.read()
            if data == config.INSTANCE_ID:
                lock_file_handle.seek(0)
                lock_file_handle.truncate()
            print('Did release_upload_lock')
        except IOError as e:
            print('release_upload_lock failed: %s' % e)
            # will quit any way, dont throw
        finally:
            fcntl.lockf(lock_file_handle, fcntl.LOCK_UN)
            if not lock_file_handle.closed:
                lock_file_handle.close()
            # 改为默认handler（退出），再触发一次
            signal.signal(_signum, signal.SIG_DFL)
            os.kill(os.getpid(), _signum)

    def check_update(data):
        if not data:
            return False
        for data_item in data:
            result = data_item.get('result', None)
            if not result:
                continue
            if result.get('updated', []) or result.get('added', []):
                return True
        return False

    has_update = params.get('force_update', False)
    has_update = has_update or check_update(data_to_upload)

    signal.signal(signal.SIGUSR1, sig_quit)
    signal.signal(signal.SIGTERM, sig_quit)
    signal.signal(signal.SIGUSR2, sig_quit)
    signal.signal(signal.SIGINT, sig_quit)

    skip_upload_appstore = params['skip_mode'] == 'upload'
    if has_update and not params['dry_run']:
        if not skip_upload_appstore:
            itms = params['itms'] if params['itms'] else  transporter_path
            try:
                acquire_upload_lock()
            except Exception as e:
                raise e

            try:
                subprocess.check_call([
                    itms,
                    '-v', params['log_level'],
                    '-m', 'upload',
                    '-u', username,
                    '-p', password,
                    '-f', p.as_posix()])
            except:
                print('上传失败：%s.' % sys.exc_info()[0])
                raise
            finally:
                release_upload_lock()
                if not lock_file_handle.closed:
                    lock_file_handle.close()
    else:
        print('Not updates or --dry-run, will upload nothing to AppStore.')
    if not lock_file_handle.closed:
        lock_file_handle.close()
    all_handlers.handle(data_to_upload, params)
    return data_to_upload
