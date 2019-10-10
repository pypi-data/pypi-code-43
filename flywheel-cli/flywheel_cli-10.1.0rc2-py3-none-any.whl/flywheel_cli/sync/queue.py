import datetime
import logging
import sys

import fs.filesize

from ..importers.work_queue import Task, WorkQueue
from ..importers.progress_reporter import ProgressReporter
from ..util import confirmation_prompt


log = logging.getLogger(__name__)


class SyncQueue(WorkQueue):
    def __init__(self, jobs, dst, assume_yes=False, dry_run=False):
        super().__init__({'store': jobs, 'delete': 1})
        self.dst = dst
        self.assume_yes = assume_yes
        self.dry_run = dry_run
        self._progress_thread = SyncProgressReporter(self)
        self._progress_thread.add_group('store', 'Syncing', 0)
        self._progress_thread.add_group('delete', 'Deleting', 0)

    def store(self, src_file, dst_file):
        if dst_file is None:
            self.enqueue(StoreTask('create', src_file, self.dst.file, dry_run=self.dry_run))
            self._progress_thread.groups['store'].total_bytes += src_file.size
        elif src_file.size == dst_file.size and src_file.modified <= dst_file.modified:
            log.debug('Skip updating "%s"', src_file.name)
        elif self.assume_yes or self.confirm(f'Are you sure you want to replace "{src_file.name}"?'):
            self.enqueue(StoreTask('update', src_file, dst_file, dry_run=self.dry_run))
            self._progress_thread.groups['store'].total_bytes += src_file.size

    def delete(self, dst_file):
        self.enqueue(DeleteTask(dst_file, dry_run=self.dry_run))

    def enqueue(self, task, priority=10):
        super().enqueue(task, priority=priority)
        self._progress_thread.groups[task.group].total_count += 1

    def confirm(self, message):
        self._progress_thread.suspend()
        confirm = confirmation_prompt(message)
        self._progress_thread.resume()
        return confirm

    def start(self):
        super().start()
        self._progress_thread.start()

    def shutdown(self):
        self._progress_thread.shutdown()
        self._progress_thread.final_report()
        super().shutdown()


class StoreTask(Task):
    # TODO doc
    def __init__(self, action, src_file, dst_file, dry_run=False):
        super().__init__('store')
        self.action = action
        self.src_file = src_file
        self.dst_file = dst_file
        self.dry_run = dry_run

    def execute(self):
        """Store source read()-able on dest and cleanup locally unzipped slice (if unpacked)"""
        log.debug(self.get_desc())
        if not self.dry_run:
            if callable(self.dst_file):  # create new dst file
                self.dst_file = self.dst_file(self.src_file.name)
            self.dst_file.store(self.src_file)
            self.src_file.cleanup()
        return None, None

    def get_bytes_processed(self):
        """Return number of bytes read from the source (equals bytes written to destination)"""
        return self.src_file.bytes_read

    def get_desc(self):
        """create|update path/to/file"""
        return f'{self.action} {self.src_file.name}'


class DeleteTask(Task):
    def __init__(self, dst_file, dry_run=False):
        super().__init__('delete')
        self.dst_file = dst_file
        self.dry_run = dry_run

    def execute(self):
        """Delete file on destination"""
        log.debug(self.get_desc())
        if not self.dry_run:
            self.dst_file.delete()
        return None, None

    def get_bytes_processed(self):
        """Return one (representing a single file instead of bytes)"""
        return 1

    def get_desc(self):
        """delete path/to/file"""
        return f'delete {self.dst_file.name}'


class SyncProgressReporter(ProgressReporter):
    def report(self, newline='\r'):
        messages = []
        estimate = None
        for name, group in self.groups.items():
            if group.total_count > 0:
                if group.completed == group.total_count:  # NOTE not using skip mechanism
                    speed_str = 'DONE'
                elif name == 'store':
                    speed_str = fs.filesize.traditional(group.bytes_per_sec) + '/s'
                    if group.completed > 0:
                        elapsed = (datetime.datetime.now() - self._start_time).total_seconds()
                        file_speed = group.completed / elapsed
                        byte_speed = group.completed_bytes / elapsed
                        files_left = group.total_count - group.completed
                        bytes_left = group.total_bytes - group.completed_bytes
                        estimate = (files_left / file_speed) + (bytes_left / byte_speed) / 2
                elif name == 'delete':
                    # NOTE reusing group.bytes_per_sec for tracking deleted / sec
                    # TODO in-depth subclassing of WorkQueue for appropriate attribute name
                    speed_str = f'{group.bytes_per_sec:.2f}/s'
                messages.append(f'{group.desc} {group.completed}/{group.total_count} - {speed_str}')

        if estimate is not None:
            messages.append('ETA: ' + self.format_timedelta(datetime.timedelta(seconds=estimate)))

        message = ', '.join(messages).ljust(self.columns) + newline
        sys.stdout.write(message)
        sys.stdout.flush()

    def final_report(self):
        self.sample()
        self.report(newline='\n')
        if self.groups['store'].completed > 0:
            xfer_bytes = fs.filesize.traditional(self.groups['store'].completed_bytes)
            xfer_time = self.format_timedelta(datetime.datetime.now() - self._start_time)
            print(f'Transferred {xfer_bytes} in {xfer_time}')
        else:
            print('Nothing transferred - destination is up to date')
        if self.groups['delete'].completed > 0:
            deleted_count = self.groups['delete'].completed
            print(f'Deleted {deleted_count} files on destination')

    @staticmethod
    def format_timedelta(timedelta):
        """Return human-readable str given a datetime.timedelta"""
        seconds = timedelta.total_seconds()
        if seconds < 60:
            return f'{seconds:.2f} seconds'
        return str(datetime.timedelta(seconds=int(seconds)))
