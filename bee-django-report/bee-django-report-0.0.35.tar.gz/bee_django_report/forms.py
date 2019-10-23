# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms

from .models import MentorScoreWeek,Report

class MentorScoreWeekForm(forms.ModelForm):
    class Meta:
        model = MentorScoreWeek
        fields = ['year', "week", "score", "info"]

    # def update_rank(self):


class UserServerForm(forms.Form):
    status = forms.ChoiceField(label='学生状态',choices=((0,'全部'),(1,"正常")),required=False)
    server = forms.ModelChoiceField(queryset=Report.get_server_list(), label='客服',required=False)


class UserSectionForm(forms.Form):
    status = forms.ChoiceField(label='学生状态',choices=((0,'全部'),(1,"正常")),required=False)
    expire_date_start=forms.CharField(label='结课开始日',required=False)
    expire_date_end=forms.CharField(label='结课结束日',required=False)


    def __init__(self, user, *args, **kwargs):
        super(UserSectionForm, self).__init__(*args, **kwargs)
        mentor_queryset = Report.get_assistant_list(user)
        user_class_queryset = Report.get_class_list(user)
        if mentor_queryset.exists():
            self.fields['assistant'] = forms.ModelChoiceField(queryset=mentor_queryset, label='助教', required=False)
        if user_class_queryset.exists():
            self.fields['user_class'] = forms.ModelChoiceField(queryset=user_class_queryset, label='班级', required=False)
            # self.initial['assistant'] = kwargs["instance"].userprofile.lecturer