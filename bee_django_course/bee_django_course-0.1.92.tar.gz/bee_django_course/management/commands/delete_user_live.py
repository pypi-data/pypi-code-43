# -*- coding:utf-8 -*-
import time, datetime
from django.core.management.base import BaseCommand
from bee_django_course.models import UserLive
from django.utils import timezone

from bee_django_course import cc


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('days', type=int, nargs='?', default=20)

    def handle(self, *args, **options):
        # 默认删除20天前的录播
        days = options["days"]
        for e in UserLive.objects.filter(created_at__lt=timezone.now() - datetime.timedelta(days=days), status=1):
            if e.provider_name == u'cc':
                if e.record_video_id and e.record_status == '10':
                    cc.delete_video(e.record_video_id)
                    time.sleep(1)
            elif e.provider_name == u'gensee':
                pass
            elif e.provider_name == u'tencent':
                pass
            e.status = 2
            e.save()

        return
