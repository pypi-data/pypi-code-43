from sync.album import AlbumSync
from sync.board import NoticeSync
from sync.course import CourseTableSync
from sync.news import NewsSync
from sync.video import VideoSync


def start_sync():
    course_table_sync = CourseTableSync()
    course_table_sync.start()
