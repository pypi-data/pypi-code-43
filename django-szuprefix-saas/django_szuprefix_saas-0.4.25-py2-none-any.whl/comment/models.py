# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_szuprefix_saas.saas.models import Party


class Comment(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "评论"
        permissions = (
            ("view_all_comment", "查看所有评论"),
        )

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="comments", null=True, on_delete=models.PROTECT)
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, related_name="comments")
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_name = models.CharField("名称", max_length=256, db_index=True, null=True, blank=True)
    content = models.TextField("内容")
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    is_active = models.BooleanField("有效", default=True)

    def save(self, **kwargs):
        if not self.object_name:
            self.object_name = unicode(self.content_object)
        return super(Comment, self).save(**kwargs)

    def __unicode__(self):
        return "%s 评论 %s" % (self.user.get_full_name(), self.content_object)
