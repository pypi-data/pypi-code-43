# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django_szuprefix.api.mixins import IDAndStrFieldSerializerMixin
from django_szuprefix.utils.datautils import auto_code
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from . import models
from ..saas.mixins import PartySerializerMixin


class CourseSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    category_name = serializers.CharField(source="category", read_only=True)

    # chapters = serializers.ManyRelatedField
    # exam_papers_name = serializers.CharField(label="试卷", read_only=True)
    class Meta:
        model = models.Course
        exclude = ('party',)
        validators = [
            UniqueTogetherValidator(
                queryset=models.Course.objects.all(),
                fields=('party', 'name'),
                message='相同名称的记录已存在, 请不要重复创建.'
            )
        ]

    def validate_code(self, value):
        if value is None:
            value = auto_code(self.validated_data['name'])
        return value


class CourseNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ('name',)


class CategorySerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Category
        exclude = ('party',)
        validators = [
            UniqueTogetherValidator(
                queryset=models.Category.objects.all(),
                fields=['party', 'name'],
                message='相同记录已存在, 请不要重复创建.'
            )
        ]


class ChapterSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    course_name = serializers.CharField(source="course", read_only=True)

    # exam_papers_name = serializers.CharField(label="试卷", read_only=True)
    class Meta:
        model = models.Chapter
        exclude = ('party', 'order_num')
        validators = [
            UniqueTogetherValidator(
                queryset=models.Chapter.objects.all(),
                fields=['course', 'name'],
                message='相同记录已存在, 请不要重复创建.'
            )
        ]
