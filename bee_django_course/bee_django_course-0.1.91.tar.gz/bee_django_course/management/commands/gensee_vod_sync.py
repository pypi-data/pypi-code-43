# coding=utf-8
__author__ = 'bee'
import os, datetime, json

from django.core.management.base import BaseCommand, CommandError
from bee_django_course.utils import gensee_vod_sync


class Command(BaseCommand):
    def handle(self, *args, **options):
        sync_count = gensee_vod_sync()
        return sync_count
