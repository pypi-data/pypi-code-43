# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime, os, csv
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.utils.timezone import localtime
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import AdminPasswordChangeForm
from PIL import Image, ExifTags
from django.contrib.contenttypes.models import ContentType
# from bee_django_crm.models import PreUser

from .decorators import cls_decorator, func_decorator
from .models import UserProfile, UserSN, UserProfileParentRelation, UserClass, UserLeaveRecord, LOCAL_TIMEZONE
from .forms import UserForm, UserProfileParentsForm, UserAvatarForm, UserSearchForm, profile_inline_formset, \
    UserClassForm, UserClassDashBoardSearchForm, \
    UserClassSearchForm, UserGroupForm, \
    UserSNForm, \
    UserLeaveRecordForm, \
    UserLeaveRecordCancelForm
from .utils import export_csv

User = get_user_model()


# Create your views here.
def test(request):
    # a=u.userprofile.is_assistant()
    # print(a)
    # if hasattr(settings,"GENSEE_CONFIG"):
    # print(b)
    #     print(settings.GENSEE_CONFIG.genseeUrl)
    # try:
    #     a=settings.aaa
    #     print('====')
    # except:
    #     print('222')

    return HttpResponse("OK")


def home_page(request):
    return render(request, 'bee_django_user/home_page.html')


# ========user 学生===========
@method_decorator(cls_decorator(cls_name='UserList'), name='dispatch')
class UserList(ListView):
    model = User
    template_name = 'bee_django_user/user/list.html'
    context_object_name = 'user_list'
    paginate_by = 20
    queryset = None

    def search(self):
        # if self.request.user.has_perm("bee_django_user.view_all_users"):
        #     queryset = User.objects.all().order_by('userprofile__student_id')
        # else:
        #     if self.request.user.has_perm("bee_django_user.view_teach_users"):
        #         filter1 = Q(userprofile__user_class__assistant=self.request.user)
        #     else:
        #         filter1 = Q(pk=None)
        #     if self.request.user.has_perm("bee_django_user.view_child_users"):
        #         filter2 = Q(userprofile__parents=self.request.user.userprofile)
        #     else:
        #         filter2 = Q(pk=None)
        #     queryset = User.objects.filter(filter1 | filter2).order_by('id').distinct()
        queryset = self.request.user.get_student_list()
        id = self.request.GET.get("id")
        status = self.request.GET.get("status")
        student_id = self.request.GET.get("student_id")
        first_name = self.request.GET.get("first_name")
        group_id = self.request.GET.get("group")
        start_expire_date = self.request.GET.get("start_expire_date")
        end_expire_date = self.request.GET.get("end_expire_date")
        if not id in [0, "0", None]:
            queryset = queryset.filter(pk=id)
        if not status in [0, "0", None]:
            if status == "1":
                queryset = queryset.filter(is_active=True, userprofile__is_pause=False).exclude(
                    userleavestatus__status=1)
            elif status == "2":
                queryset = queryset.filter(userprofile__is_pause=True)
            elif status == "3":
                queryset = queryset.filter(is_active=False)
            elif status == "999":
                queryset = queryset.filter(userleavestatus__status=1)
        if student_id:
            queryset = queryset.filter(userprofile__student_id=student_id)
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if group_id:
            queryset = queryset.filter(groups__id__in=[group_id])
        if start_expire_date:
            queryset = queryset.filter(userprofile__expire_date__gte=start_expire_date)
        if end_expire_date:
            queryset = queryset.filter(userprofile__expire_date__lte=end_expire_date)
        self.queryset = queryset
        return self.queryset

    # def get_queryset(self):
    #     queryset = []
    #     if self.request.user.has_perm("bee_django_user.view_all_users"):
    #         queryset = User.objects.all().order_by('id')
    #     elif self.request.user.has_perm("bee_django_user.view_teach_users"):
    #         queryset = User.objects.filter(userprofile__user_class__assistant=self.request.user).order_by('id')
    #     else:
    #         self.queryset=[]
    #         return self.queryset
    #
    #     student_id = self.request.GET.get("student_id")
    #     first_name = self.request.GET.get("first_name")
    #     group_id = self.request.GET.get("group")
    #     if student_id:
    #         queryset = queryset.filter(userprofile__student_id=student_id)
    #     if first_name:
    #         queryset = queryset.filter(first_name__icontains=first_name)
    #     if group_id:
    #         queryset = queryset.filter(groups__id__in=[group_id])
    #     self.queryset=queryset
    #     return self.queryset

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)
        status = self.request.GET.get("status")
        student_id = self.request.GET.get("student_id")
        first_name = self.request.GET.get("first_name")
        group = self.request.GET.get("group")
        start_expire_date = self.request.GET.get("start_expire_date")
        end_expire_date = self.request.GET.get("end_expire_date")

        context['search_form'] = UserSearchForm(
            {"status": status, "student_id": student_id, "first_name": first_name, "group": group,
             "start_expire_date": start_expire_date,
             "end_expire_date": end_expire_date})
        return context

    def get_csv_info(self, user):
        return [
            user.userprofile.get_sn(),
            user.username,
            user.first_name,
            user.userprofile.preuser.get_gender(),
            user.userprofile.preuser.mobile,
            user.userprofile.preuser.wx,
            user.userprofile.preuser.birthday,
            user.userprofile.preuser.get_source(),
            user.userprofile.preuser.province,
            user.userprofile.preuser.city,

        ]

    def get_csv_headers(self):
        return [
            '序号'.encode('utf-8'),
            '缦客号'.encode('utf-8'),
            '用户名'.encode('utf-8'),
            '姓名'.encode('utf-8'),
            '性别'.encode('utf-8'),
            '电话'.encode('utf-8'),
            '微信'.encode('utf-8'),
            '出生日期'.encode('utf-8'),
            '来源'.encode('utf-8'),
            '省'.encode('utf-8'),
            '市'.encode('utf-8'),

        ]

    def get(self, request, *args, **kwargs):
        self.queryset = self.search()
        if request.GET.get("export"):
            rows = ([(i + 1).__str__()] + self.get_csv_info(user) for i, user in enumerate(self.queryset))
            return export_csv('用户信息'.encode('utf-8'), self.get_csv_headers(), rows)
        else:
            return super(UserList, self).get(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='UserDetail'), name='dispatch')
class UserDetail(DetailView):
    model = User
    template_name = 'bee_django_user/user/detail.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super(UserDetail, self).get_context_data(**kwargs)
        if "cc" in settings.COURSE_LIVE_PROVIDER_LIST:
            context["cc"] = True
        if "gensee" in settings.COURSE_LIVE_PROVIDER_LIST:
            context["gensee"] = True
        return context


class UserDelete(DeleteView):
    model = User
    success_url = reverse_lazy('bee_django_user:user_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# @method_decorator(cls_decorator(cls_name='UserCreate'), name='dispatch')
# class UserCreate(TemplateView):
#     # model = User
#     # form_class = UserCreateForm
#     template_name = 'bee_django_user/user/create.html'
#     # success_url = reverse_lazy('bee_django_user:user_list')
#
#     # def get_context_data(self, **kwargs):
#     #     context = super(UserCreate, self).get_context_data(**kwargs)
#     #     context["preuser"] = PreUser.objects.get(id=self.kwargs["preuser_id"])
#     #     return context
#
#     @transaction.atomic
#     def _create_user(self, preuser, preuser_fee_id):
#         try:
#             # 学号
#             max_student_id = UserProfile.get_max_student_id()
#             user_profile = UserProfile()
#             user_profile.preuser = preuser
#             user_profile.student_id = max_student_id + 1
#             # sn
#             max_sn = UserProfile.get_max_sn()
#             sn = UserSN.get_next_sn(max_sn)
#             if not sn:
#                 messages.error(self.request, '统一缦客号生成错误')
#                 return
#             user_profile.sn = sn
#             user_profile.save()
#             # user_profile.create_user(preuser_fee_id)
#             user = user_profile.user
#             # res, msg = after_check_callback(preuser_fee_id, user=user, new_user=True)
#             messages.success(self.request, '添加用户成功')
#         except Exception as e:
#             print(e)
#             messages.error(self.request, '发生错误')
#
#     @transaction.atomic
#     def get(self, request, *args, **kwargs):
#         # print(self.kwargs)
#         preuser_id = request.GET["preuser_id"]
#         preuser_fee_id = request.GET["preuser_fee_id"]
#         if not self.request.user.has_perm('bee_django_user.add_userprofile'):
#             messages.error(self.request, '没有权限')
#             return redirect(reverse('bee_django_crm:preuser_fee_detail', kwargs={"pk": preuser_fee_id}))
#         # preuser = PreUser.objects.get(id=preuser_id)
#         try:
#             user_profile = preuser.userprofile
#             user = user_profile.user
#             if preuser_fee_id:
#                 res, msg = after_check_callback(preuser_fee_id, user=user, new_user=False)
#                 messages.success(self.request, '已添加过用户，后续操作成功')
#             else:
#                 messages.success(self.request, '已添加过用户')
#         except UserProfile.DoesNotExist:
#             self._create_user(preuser, preuser_fee_id)
#         except:
#             messages.success(self.request, '发生错误')
#
#         if preuser.level == 3:
#             return redirect(reverse('bee_django_crm:preuser_fee_list', kwargs={'preuser_id': 0}))
#         elif preuser.level == 4:
#             return redirect(reverse('bee_django_crm:preuser_list') + "?level=4")
#
#         return

# class CodeUserCreate(TemplateView):
#     template_name = 'bee_django_user/user/create.html'
#
#     @transaction.atomic
#     def get(self, request, *args, **kwargs):
#         # print(self.kwargs)
#         preuser_id = request.GET["preuser_id"]
#         if not self.request.user.has_perm('bee_django_user.add_userprofile'):
#             messages.error(self.request, '没有权限')
#             return redirect(reverse('bee_django_crm:preuser_list') + "?level=4")
#         preuser = PreUser.objects.get(id=preuser_id)
#         try:
#             user_profile = preuser.userprofile
#             user = user_profile.user
#             messages.error(self.request, '已创建过账号')
#             return redirect(reverse('bee_django_user:detail', kwargs={'pk': user.id}))
#         except UserProfile.DoesNotExist:
#             try:
#                 # student_id
#                 max_student_id = get_max_student_id()
#                 user_profile = UserProfile()
#                 user_profile.preuser = preuser
#                 user_profile.student_id = max_student_id + 1
#                 # sn
#                 max_sn = get_max_sn()
#                 sn = UserSN.get_next_sn(max_sn)
#                 if not sn:
#                     messages.error(self.request, '统一缦客号生成错误')
#                     return redirect(reverse('bee_django_crm:preuser_list') + "?level=4")
#                 user_profile.sn = sn
#                 user_profile.save()
#                 user = user_profile.user
#                 messages.success(self.request, '添加用户成功')
#             except Exception as e:
#                 print(e)
#                 messages.error(self.request, '发生错误')
#
#         return redirect(reverse('bee_django_crm:preuser_list') + "?level=4")


@method_decorator(cls_decorator(cls_name='UserUpdate'), name='dispatch')
# @method_decorator(permission_required("change_user"), name='dispatch')
class UserUpdate(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'bee_django_user/user/form.html'

    def get_success_url(self):
        return reverse_lazy("bee_django_user:user_detail", kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserUpdate, self).get_context_data(**kwargs)
        context["formset"] = profile_inline_formset(instance=self.object)
        return context

    def get_form_kwargs(self):
        kwargs = super(UserUpdate, self).get_form_kwargs()
        user = User.objects.get(id=self.kwargs["pk"])
        kwargs.update({
            'userprofile': user.userprofile
        })
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        if not self.request.user.has_perm('bee_django_user.change_userprofile'):
            messages.error(self.request, '没有权限')
            return redirect(reverse('bee_django_user:user_update', kwargs=self.kwargs))
        formset = profile_inline_formset(self.request.POST, self.request.FILES, instance=self.object)
        if formset.is_valid():
            # profile = formset.cleaned_data[0]
            try:
                agent = form.cleaned_data['agent']
                # form.instance.agent = agent
                self.object.userprofile.agent = agent
            except KeyError:
                pass


            try:
                lecturer = form.cleaned_data['lecturer']
                self.object.userprofile.lecturer = lecturer
            except KeyError:
                pass

            # profile.agent=agent
            # print(agent)
            # agent = profile['agent']
            # print(agent)
            self.object.userprofile.save()
            self.object.userprofile.update_lecturer_agent()
            messages.success(self.request, '修改成功')
        return super(UserUpdate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='UserUpdate'), name='dispatch')
class UserGroupUpdate(UpdateView):
    model = User
    form_class = UserGroupForm
    template_name = 'bee_django_user/group/user_group_form.html'

    def get_success_url(self):
        return reverse_lazy("bee_django_user:user_detail", kwargs=self.kwargs)


class UserSNUpdate(UpdateView):
    model = UserProfile
    form_class = UserSNForm
    template_name = 'bee_django_user/user/user_sn_form.html'

    def get_success_url(self):
        user_profile_id = self.kwargs['pk']
        user = User.objects.get(userprofile__id=user_profile_id)
        return reverse_lazy("bee_django_user:user_detail", kwargs={"pk": user.id})

    def get_context_data(self, **kwargs):
        context = super(UserSNUpdate, self).get_context_data(**kwargs)
        context["sn_list"] = UserSN.objects.all()
        user_profile_id = self.kwargs['pk']
        user = User.objects.get(userprofile__id=user_profile_id)
        context["user"] = user
        context["max_sn"] = UserProfile.get_max_sn()
        return context


class UserParentUpdateTemplate(TemplateView):
    template_name = 'bee_django_user/user/user_parent.html'

    def get_context_data(self, **kwargs):
        context = super(UserParentUpdateTemplate, self).get_context_data(**kwargs)
        user_id = self.kwargs['student_id']
        user = User.objects.get(id=user_id)
        context["user"] = user
        context["user_parent_relation"] = UserProfileParentRelation.objects.filter(student=user.userprofile)
        context["form"] = UserProfileParentsForm()
        return context

    def get(self, request, *args, **kwargs):
        return super(UserParentUpdateTemplate, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs['student_id']
        user = User.objects.get(id=user_id)
        form = UserProfileParentsForm(request.POST)
        if form.is_valid():
            parent = form.cleaned_data['parent']
            UserProfileParentRelation.objects.create(student=user.userprofile, parent=parent.userprofile)
            messages.success(request, '添加成功')
            # user.userprofile.parents.add(parent)
        else:
            messages.error(request, '填写错误')
        return redirect(reverse_lazy('bee_django_user:user_parent_update', kwargs=self.kwargs))


class UserParentDelete(DeleteView):
    model = UserProfileParentRelation
    success_url = reverse_lazy('bee_django_user:user_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


class UserPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('bee_django_user:user_password_change_done')
    template_name = 'bee_django_user/user/password_change.html'


class UserPasswordResetView(TemplateView):
    template_name = 'bee_django_user/user/password_reset.html'

    def get(self, request, *args, **kwargs):
        return super(UserPasswordResetView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user_id = self.kwargs['pk']
        user = User.objects.get(id=user_id)
        form = AdminPasswordChangeForm(user)
        context = super(UserPasswordResetView, self).get_context_data(**kwargs)
        context["form"] = form
        context["user"] = user
        return context

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs['pk']
        user = User.objects.get(id=user_id)
        form = AdminPasswordChangeForm(user, request.POST)
        if form.is_valid():
            if request.user.has_perm("bee_django_user.reset_user_password"):
                form.save()
                messages.success(request, '密码已经更新!')
            else:
                messages.error(request, '没有权限')
        else:
            messages.error(request, '请修正以下错误')
        return redirect(reverse_lazy('bee_django_user:user_password_reset', kwargs={'pk': user_id}))


# 用户组权限
@method_decorator(cls_decorator(cls_name='GroupList'), name='dispatch')
class GroupList(ListView):
    model = Group
    template_name = 'bee_django_user/group/list.html'
    context_object_name = 'group_list'
    paginate_by = 20


# 请假，禁用 状态

class StatusSave(TemplateView):
    def post(self, request, *args, **kwargs):
        is_pause = request.POST.get("is_pause")
        is_disable = request.POST.get("is_disable")
        user_id = request.POST.get("user_id")
        user = User.objects.get(id=user_id)
        is_pause = int(is_pause)
        is_disable = int(is_disable)
        user.is_active = True if not is_disable else False
        user.userprofile.is_pause = is_pause
        user.save()
        user.userprofile.save()
        # 发送信号
        return JsonResponse(data={
            'error': 0,
            'message': '修改成功'
        })


class AvatarUpdate(UpdateView):
    model = UserProfile
    form_class = UserAvatarForm
    template_name = 'bee_django_user/user/avatar_form.html'

    def get_success_url(self):
        user = self._get_user()
        return reverse_lazy('bee_django_user:user_detail', kwargs={"pk": user.id})

    def _get_user(self):
        userprofle = UserProfile.objects.get(id=self.kwargs["pk"])
        return userprofle.user

    def get_context_data(self, **kwargs):
        context = super(AvatarUpdate, self).get_context_data(**kwargs)
        context["user"] = self._get_user()
        return context

    @transaction.atomic
    def form_valid(self, form):
        rc = super(AvatarUpdate, self).form_valid(form)

        img = Image.open(form.instance.avatar)

        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    exif = dict(img._getexif().items())

                    if exif[orientation] == 3:
                        img = img.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        img = img.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        img = img.rotate(90, expand=True)

                    break
        except:
            pass

        thumbnail = img.resize((100, 100), Image.ANTIALIAS)
        thumbnail = thumbnail.crop((0, 0, 100, 100))
        thumbnail.save(form.instance.avatar.path)

        img.close()
        return rc


class RoomSave(TemplateView):
    def save_cc_room(self, userprofile, _type):
        try:
            from bee_django_course.cc import create_room
            if _type == 'create':
                room = create_room(userprofile.user.first_name + "的直播间")
                if room:
                    userprofile.room_id = room
                    userprofile.save()
                    return True
                return False
            elif _type == 'delete':
                return False
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def save_gensee_room(self, userprofile, _type):
        try:
            from bee_django_course.gensee import create_room, delete_room
            if _type == 'create':
                room = create_room(userprofile.user.first_name + "的直播间")
                if room:
                    userprofile.gensee_room_id = room
                    userprofile.save()
                    return True
                return False
            elif _type == 'delete':
                res = delete_room(userprofile.gensee_room_id)
                if res == True:
                    userprofile.gensee_room_id = None
                    userprofile.save()
                return res
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get("user_id")
        provider_name = request.POST.get("provider")
        _type = request.POST.get("t")
        userprofile = UserProfile.objects.get(user_id=user_id)
        cc_res = False
        gensee_res = False
        if provider_name == 'cc':
            cc_res = self.save_cc_room(userprofile, _type)
        if provider_name == 'gensee':
            gensee_res = self.save_gensee_room(userprofile, _type)
        return JsonResponse(data={
            'cc_res': cc_res,
            "gensee_res": gensee_res
        })


# 请假记录
class LeaveList(ListView):
    model = UserLeaveRecord
    template_name = 'bee_django_user/leave/list.html'
    queryset = None
    context_object_name = 'record_list'
    paginate_by = 20

    def get_user(self):
        return User.objects.get(id=self.kwargs["user_id"])

    def get_queryset(self):
        user = self.get_user()
        return UserLeaveRecord.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super(LeaveList, self).get_context_data(**kwargs)
        context["user"] = self.get_user()
        return context


class LeaveDetail(DetailView):
    model = UserLeaveRecord
    template_name = 'bee_django_user/leave/detail.html'
    context_object_name = 'record'


# 添加请假记录
class LeaveCreate(CreateView):
    model = UserLeaveRecord
    form_class = UserLeaveRecordForm
    template_name = 'bee_django_user/leave/form.html'
    success_url = None

    def get_success_url(self):
        return reverse_lazy('bee_django_user:leave_list', kwargs=self.kwargs)

    def get_user(self):
        return User.objects.get(id=self.kwargs["user_id"])

    def get_context_data(self, **kwargs):
        context = super(LeaveCreate, self).get_context_data(**kwargs)

        context["user"] = self.get_user()
        return context

    def form_valid(self, form):
        days = None
        user = self.get_user()
        user_profile = user.userprofile
        form.instance.user = user
        if form.instance.end and form.instance.start:
            days = form.instance.end - form.instance.start
        form.instance.old_expire = user_profile.expire_date
        form.instance.created_by = self.request.user

        _info = ''
        # 请假
        if form.instance.type in [1]:
            if not days or days.days < 0:
                messages.error(self.request, '开始日期或结束日期填写错误')
                return redirect(reverse_lazy('bee_django_user:leave_add', kwargs=self.kwargs))
            if user_profile.expire_date:
                form.instance.new_expire = (user_profile.expire_date + datetime.timedelta(days=days.days))
            else:
                messages.error(self.request, '请先填写该学生结课日期，或选择【延期/提前】类型')
                return redirect(reverse_lazy('bee_django_user:leave_add', kwargs=self.kwargs))
            _info = '请假'
        # if form.instance.type in [2]:
        #     if user_profile.expire_date:
        #         form.instance.new_expire = (user_profile.expire_date - datetime.timedelta(days=days.days))
        # 延期/提前
        if form.instance.type in [3]:
            _info = '延期'
            form.instance.new_expire = form.instance.end
        if form.instance.type in [4]:
            _info = '提前'
            form.instance.new_expire = form.instance.end

        # 详情
        info = '<p>=====以下由【' + self.request.user.first_name + '】于【' + datetime.datetime.now(
            tz=LOCAL_TIMEZONE).strftime("%Y-%m-%d %H:%M") + '】添加' + _info + '=====</p>'
        info += "<p>" + _info + "开始日期：" + localtime(form.instance.start).strftime("%Y-%m-%d %H:%M")
        info += "<p>" + _info + "结束日期：" + localtime(form.instance.end).strftime("%Y-%m-%d %H:%M")
        info += "<p>原结课日期：" + localtime(user.userprofile.expire_date).strftime("%Y-%m-%d %H:%M")
        info += "<p>新结课日期：" + localtime(form.instance.new_expire).strftime("%Y-%m-%d %H:%M")
        info += "<p>" + form.instance.info + "</p>"
        form.instance.info = info
        return super(LeaveCreate, self).form_valid(form)


# 审核请假
class LeaveUpdateCheck(TemplateView):
    def post(self, request, *args, **kwargs):
        record_id = self.request.POST.get('record_id')
        if not request.user.has_perm("bee_django_user.change_check"):
            return JsonResponse(data={
                'error': 1,
                'message': '没有权限'
            })
        record = UserLeaveRecord.objects.get(id=record_id)
        if record.is_check == True:
            return JsonResponse(data={
                'error': 1,
                'message': '已审核过'
            })
        record.is_check = True
        record.check_at = datetime.datetime.now()
        record.check_by = self.request.user
        record.save()

        return JsonResponse(data={
            'error': 0,
            'message': '审核成功'
        })


# 销假
class LeaveCancel(TemplateView):
    model = UserLeaveRecord
    template_name = 'bee_django_user/leave/form_cancel.html'

    def get_record(self):
        record = UserLeaveRecord.objects.get(id=self.kwargs["pk"])
        return record

    def get_context_data(self, **kwargs):
        context = super(LeaveCancel, self).get_context_data(**kwargs)
        record = UserLeaveRecord.objects.get(id=self.kwargs["pk"])
        context["record"] = record
        context["form"] = UserLeaveRecordCancelForm()
        context["temp_end_start"] = record.end - datetime.timedelta(days=1)
        return context

    def post(self, request, *args, **kwargs):
        form = UserLeaveRecordCancelForm(request.POST)
        if form.is_valid():
            record = self.get_record()
            user = record.user
            user_profile = user.userprofile
            s_days = form.instance.start - record.start
            e_days = record.end - form.instance.start

            if s_days.days < 0 or e_days.days <= 0:
                messages.error(request, '开始日期填写错误')
                return redirect(reverse_lazy('bee_django_user:leave_cancel', kwargs=self.kwargs))
            if not user_profile.expire_date:
                messages.error(request, '请先填写该学生结课日期，或选择【延期/提前】类型')
                return redirect(reverse_lazy('bee_django_user:leave_add', kwargs={"user_id": user.id}))
            record.new_expire = (user_profile.expire_date - datetime.timedelta(days=e_days.days))
            record.type = 2
            record.end = form.instance.start
            info = record.info + '<p>=====以下由【' + request.user.first_name + '】于【' + datetime.datetime.now(
                tz=LOCAL_TIMEZONE).strftime("%Y-%m-%d %H:%M") + '】添加销假=====</p>'
            info += "<p>结束休假日期：" + form.instance.start.strftime("%Y-%m-%d")
            info += "<p>原结课日期：" + localtime(user.userprofile.expire_date).strftime("%Y-%m-%d %H:%M")
            info += "<p>新结课日期：" + localtime(record.new_expire).strftime("%Y-%m-%d %H:%M")
            info += "<p>" + form.instance.info + "</p>"
            record.info = info
            record.save()
            return redirect(reverse_lazy('bee_django_user:leave_list', kwargs={"user_id": user.id}))
        else:
            messages.error(request, '出错了')
            return redirect(reverse_lazy('bee_django_user:leave_cancel', kwargs=self.kwargs))
            # return super(LeaveCancel, self).form_valid(form)


class LeaveDelete(DeleteView):
    model = UserLeaveRecord
    success_url = None

    def get_success_url(self):
        record = UserLeaveRecord.objects.get(id=self.kwargs["pk"])
        return reverse_lazy('bee_django_user:leave_list', kwargs={"user_id": record.user.id})

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# ========class 班级===========
@method_decorator(cls_decorator(cls_name='ClassList'), name='dispatch')
class ClassList(ListView):
    model = UserClass
    template_name = 'bee_django_user/class/list.html'
    context_object_name = 'class_list'
    paginate_by = 20

    def search(self):
        # if self.request.user.has_perm("bee_django_user.view_all_classes"):
        #     queryset = UserClass.objects.all()
        # elif self.request.user.has_perm("bee_django_user.view_teach_classes"):
        #     queryset = UserClass.objects.filter(assistant=self.request.user)
        # else:
        #     return UserClass.objects.none()
        queryset = self.request.user.userprofile.get_class_list()
        status = self.request.GET.get("status")
        class_name = self.request.GET.get("class_name")
        assistant_name = self.request.GET.get("assistant_name")

        if not status in [0, "0", None]:
            queryset = queryset.filter(status=status)

        if not class_name in [0, "0", None]:
            queryset = queryset.filter(name__icontains=class_name)
        if assistant_name:
            try:
                kwargs = {}  # 动态查询的字段
                name_field = settings.USER_NAME_FIELD
                kwargs["assistant__" + name_field + '__icontains'] = assistant_name
                queryset = queryset.filter(**kwargs)
            except:
                queryset = queryset

        return queryset

    def get_queryset(self):
        return self.search()

    def get_context_data(self, **kwargs):
        context = super(ClassList, self).get_context_data(**kwargs)
        status = self.request.GET.get("status")
        class_name = self.request.GET.get("class_name")
        assistant_name = self.request.GET.get("assistant_name")

        context['search_form'] = UserClassSearchForm(
            {"status": status, "class_name": class_name, "assistant_name": assistant_name})
        return context


class ClassDashboard(ClassList):
    template_name = 'bee_django_user/class/dashboard.html'
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super(ClassDashboard, self).get_context_data(**kwargs)
        status = self.request.GET.get("status")
        class_name = self.request.GET.get("class_name")
        time = self.request.GET.get("time")  # 时间段
        context['search_form'] = UserClassDashBoardSearchForm(
            {"status": status, "class_name": class_name, "time": time})
        context["time"] = time
        return context


@method_decorator(cls_decorator(cls_name='ClassDetail'), name='dispatch')
class ClassDetail(DetailView):
    model = UserClass
    template_name = 'bee_django_user/class/detail.html'
    context_object_name = 'class'

    # def get_context_data(self, **kwargs):
    #     context=super(ClassDetail,self).get_context_data(kwargs)
    #     context["students"]=None
    #     return context


@method_decorator(cls_decorator(cls_name='ClassCreate'), name='dispatch')
class ClassCreate(CreateView):
    model = UserClass
    form_class = UserClassForm
    template_name = 'bee_django_user/class/form.html'
    success_url = reverse_lazy('bee_django_user:class_list')


@method_decorator(cls_decorator(cls_name='ClassUpdate'), name='dispatch')
class ClassUpdate(UpdateView):
    model = UserClass
    form_class = UserClassForm
    template_name = 'bee_django_user/class/form.html'
    success_url = reverse_lazy('bee_django_user:class_list')

    @transaction.atomic
    def form_valid(self, form):
        if not self.request.user.has_perm('bee_django_user.change_userclass'):
            messages.error(self.request, '没有权限')
            return redirect(reverse('bee_django_user:class_update', kwargs=self.kwargs))
        return super(ClassUpdate, self).form_valid(form)

        #
        # def get_context_data(self, **kwargs):
        #     context = super(UserUpdate, self).get_context_data(**kwargs)
        #     context["formset"] = profile_inline_formset(instance=self.object)
        #     return context
        #
        # @transaction.atomic
        # def form_valid(self, form):
        #     formset = profile_inline_formset(self.request.POST, instance=self.object)
        #     if formset.is_valid():
        #         profile = formset.cleaned_data[0]
        #         room_id = profile['room_id']
        #         self.object.userprofile.room_id = room_id
        #         self.object.userprofile.save()
        #     return super(UserUpdate, self).form_valid(form)


class UserPermisionResetTemplate(TemplateView):
    template_name = 'bee_django_user/user/permission_reset.html'
    csvFile = None
    reader = None
    error_list = []

    def _get_path(self):
        return os.path.join(settings.BASE_DIR, "Permission.csv")

    def _load_csv(self):
        _path = self._get_path()
        if not os.path.exists(_path):
            return None, '没有找到csv文件'
        try:
            self.csvFile = open(_path, "r")
            reader = csv.reader(self.csvFile)  # 返回的是迭代类型
            return reader, ''
        except Exception as e:
            return None, e.__str__()

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            self.error_list = [
                {"app_label": "", "model": "", "codename": "", "msg": "没有超级管理员权限"}]
            return super(UserPermisionResetTemplate, self).get(request, *args, **kwargs)
        self.reader, errmsg = self._load_csv()
        error_list = []
        group_list = []
        for i, item in enumerate(self.reader):
            if i == 0:
                continue
            elif i == 1:
                for column_id in range(6, len(item)):
                    group, is_create = Group.objects.get_or_create(name=item[column_id].__str__())
                    group_list.append({"column_id": column_id, "group": group})
            else:
                try:
                    ct = ContentType.objects.get(app_label=item[3], model=item[4])
                    permision = Permission.objects.get(content_type=ct, codename=item[5])
                except Exception as e:
                    self.error_list.append(
                        {"app_label": item[3], "model": item[4], "codename": item[5], "msg": e.__str__()})
                    continue
                for _dict in group_list:
                    column_id = int(_dict["column_id"])
                    group = _dict["group"]
                    if item[column_id] == 'v':
                        group.permissions.add(permision)
                    else:
                        group.permissions.remove(permision)
        self.csvFile.close()

        return super(UserPermisionResetTemplate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserPermisionResetTemplate, self).get_context_data(**kwargs)
        context["error_list"] = self.error_list
        return context
