# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from django.contrib.auth.models import User, Group

from .models import UserProfile, UserProfileParentRelation, UserClass, UserLeaveRecord, USER_LEAVE_TYPE_CHOICES
from django.forms.models import inlineformset_factory
from .validators import user_sn_validator


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name"]

    def __init__(self, userprofile, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        # ====设置讲师====
        lecturer_queryset = UserProfile.objects.filter(
            user__groups__name__in=UserProfile.get_lecturer_groupname_list())
        if lecturer_queryset.exists():
            # ==可添加/修改客服，讲师/没有讲师的助教/既没讲师又没班级的学生==
            if userprofile.is_role('lecturer') or (userprofile.is_role('mentor') and not userprofile.lecturer) or (
                    userprofile.is_role('student') and not userprofile.lecturer and not userprofile.user_class):
                self.fields['lecturer'] = forms.ModelChoiceField(label='讲师', queryset=lecturer_queryset, required=False)
                self.initial['lecturer'] = kwargs["instance"].userprofile.lecturer

        # ====设置客服====
        agent_queryset = UserProfile.objects.filter(user__groups__name__in=UserProfile.get_agent_groupname_list())
        if agent_queryset.exists():
            # 可添加/修改讲师，助教/没有班级的学生
            if userprofile.is_role('mentor') or (userprofile.is_role('student') and not userprofile.user_class):
                self.fields['agent'] = forms.ModelChoiceField(label='客服', queryset=agent_queryset, required=False)
                self.initial['agent'] = kwargs["instance"].userprofile.agent


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['start_date', "user_class"]


profile_inline_formset = inlineformset_factory(User, UserProfile, form=UserProfileForm, can_delete=False)


class UserAvatarForm(forms.ModelForm):
    avatar = forms.FileField(label='')

    class Meta:
        model = UserProfile
        fields = ['avatar']


class UserSearchForm(forms.Form):
    status_list = ((0, '全部'), (1, '正常'), (999, '请假'), (2, '暂停'), (3, '禁用'))
    status = forms.ChoiceField(choices=status_list, label='状态', required=False)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label='用户组', required=False)
    student_id = forms.CharField(label='学号', required=False)
    first_name = forms.CharField(label='用户姓名', required=False)
    start_expire_date = forms.CharField(label='结课日期', required=False)
    end_expire_date = forms.CharField(label='至', required=False)

    # class Meta:
    #     model = User
    #     fields = ["student_id","first_name"]


class UserProfileParentsForm(forms.Form):
    parent_queryset = User.objects.filter(groups__name__in=UserProfile.get_parent_groupname_list())
    parent = forms.ModelChoiceField(queryset=parent_queryset, label='家长助教', required=False)
    # class Meta:
    #     model = UserProfileParentRelation
    #     fields = ['parent']


class UserClassForm(forms.ModelForm):
    assistant_queryset = User.objects.filter(groups__name__in=UserProfile.get_assistant_groupname_list())
    assistant = forms.ModelChoiceField(queryset=assistant_queryset, label='助教', required=False)

    class Meta:
        model = UserClass
        fields = ["name", 'assistant', "status"]


class UserClassDashBoardSearchForm(forms.ModelForm):
    time = forms.ChoiceField(
        choices=((u"本日", '本日'), (u"昨日", '昨日'), (u"本周", '本周'), (u"上周", '上周'), (u"本月", '本月'), (u"上月", '上月')), label='时间',
        required=True)
    name = forms.CharField(label='班级名称', required=False)

    class Meta:
        model = UserClass
        fields = ['time', "status", "name"]


class UserClassSearchForm(forms.Form):
    status = forms.ChoiceField(choices=((0, '全部'), (1, '正常'), (2, "已结业"),), required=False, label='状态')
    class_name = forms.CharField(label='班级名称', required=False)
    assistant_name = forms.CharField(label='助教姓名', required=False)


class UserGroupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['groups']


class UserSNForm(forms.ModelForm):
    sn = forms.CharField(label='缦客号', validators=[user_sn_validator])

    class Meta:
        model = UserProfile
        fields = ['sn']


# 请假/延期
class UserLeaveRecordForm(forms.ModelForm):
    type_choices = ((1, "请假"), (3, "延期"))
    type = forms.ChoiceField(choices=type_choices, label='类型')

    class Meta:
        model = UserLeaveRecord
        fields = ['type', "start", "end", "info"]


# 请假/延期
class UserLeaveRecordCancelForm(forms.ModelForm):
    type_choices = ((2, "销假"),)
    type = forms.ChoiceField(choices=type_choices, label='类型')

    class Meta:
        model = UserLeaveRecord
        fields = ['type', "start", "info"]
