from allauth.account.views import SignupView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView
from django.views.generic.edit import DeleteView

from users.models import User
from .forms import InviteUserForm, InvitationSignupForm, NewDepartmentForm, DepartmentInvitationSignupForm,\
    DepartmentForm, SchoolBadgeForm
from .models import School, Faculty
from .tokens import account_activation_token
from common import common_helpers


class InviteUsers(LoginRequiredMixin, TemplateView):
    template_name = 'schools/invite-users.html'

    def get(self, request, *args, **kwargs):

        sent = kwargs.get('sent')

        invite_user_form = InviteUserForm()

        context = {
            'invite_user_form': invite_user_form,
            'sent': sent
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        if 'invite_users' in request.POST:
            invite_user_form = InviteUserForm(request.POST)
            if invite_user_form.is_valid():
                user = request.user
                school = request.user.school

                url = request.build_absolute_uri(reverse('invitation_signup'))
                uid = urlsafe_base64_encode(force_bytes(school.pk))
                token = account_activation_token.make_token(school)
                activation_link = "{0}?uid={1}&token={2}".format(url, uid, token)

                email_text = render_to_string('email/invite_users.txt', {
                    'user': user,
                    'school': school,
                    'activation_link': activation_link
                })

                to_email_address = invite_user_form.cleaned_data.get('email')
                mail_subject = 'Invitation to create an ' + settings.PROGRAM_NAME + ' account'

                email = EmailMessage(mail_subject, email_text, to=[to_email_address])

                email.send()

                return HttpResponseRedirect(reverse('schools:invite-users', args=('sent',)))

        return HttpResponseRedirect(reverse('core_nav:settings', ))


class InviteUsersDepartment(LoginRequiredMixin, TemplateView):
    template_name = 'schools/invite-users.html'

    def get(self, request, *args, **kwargs):
        sent = kwargs.get('sent')

        invite_user_form = InviteUserForm()

        context = {
            'invite_user_form': invite_user_form,
            'sent': sent
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        faculty_pk = kwargs.get('pk')

        if 'invite_users' in request.POST:

            invite_user_form = InviteUserForm(request.POST)
            if invite_user_form.is_valid():
                user = request.user
                school = request.user.school
                faculty = Faculty.objects.get(pk=faculty_pk)

                url = request.build_absolute_uri(reverse('department_invitation_signup'))
                uid = urlsafe_base64_encode(force_bytes(faculty.pk))
                faculty_token = account_activation_token.make_token(faculty)
                activation_link = "{0}?uid={1}&token={2}".format(url, uid, faculty_token)

                email_text = render_to_string('email/invite_users_departmental.txt', {
                    'user': user,
                    'school': school,
                    'activation_link': activation_link
                })

                to_email_address = invite_user_form.cleaned_data.get('email')
                mail_subject = 'Invitation to join an ' + settings.PROGRAM_NAME + ' department'

                email = EmailMessage(mail_subject, email_text, to=[to_email_address])
                email.send()

                return HttpResponseRedirect(reverse('schools:invite-users', args=('sent',)))

        return HttpResponseRedirect(reverse('schools:view-department', args=(faculty_pk,)))


class InvitationSignupView(SignupView):
    template_name = 'account/invitation-signup.html'
    form_class = InvitationSignupForm
    view_name = 'invitation_signup'

    def dispatch(self, request, *args, **kwargs):

        uid = self.request.GET.get('uid')
        token = request.GET.get('token')

        if uid is not None:
            try:
                school_id = force_text(urlsafe_base64_decode(uid))
                school = School.objects.get(pk=school_id)
                if account_activation_token.check_token(school, token):
                    self.form_class.school_id = school_id
            except(TypeError, ValueError, OverflowError, School.DoesNotExist):
                pass

        return super(InvitationSignupView, self).dispatch(request, *args, **kwargs)

invitation_signup = InvitationSignupView.as_view()



class DepartmentInvitationSignupView(SignupView):
    template_name = 'account/department-invitation-signup.html'
    form_class = DepartmentInvitationSignupForm
    view_name = 'department_invitation_signup'

    def dispatch(self, request, *args, **kwargs):

        uid = self.request.GET.get('uid')
        token = request.GET.get('token')

        if uid is not None:
            try:
                faculty_id = force_text(urlsafe_base64_decode(uid))
                faculty = Faculty.objects.get(pk=faculty_id)

                if account_activation_token.check_token(faculty, token):
                    self.form_class.faculty_id = faculty_id

                return super(DepartmentInvitationSignupView, self).dispatch(request, *args, **kwargs)

            except(TypeError, ValueError, OverflowError, Faculty.DoesNotExist):
                pass

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



department_invitation_signup = DepartmentInvitationSignupView.as_view()


class ManageDepartments(LoginRequiredMixin, TemplateView):
    template_name = 'schools/manage-departments.html'

    def get(self, request, *args, **kwargs):

        faculty_list = []
        faculties = Faculty.objects.get_school_faculties(request.user)


        for faculty in faculties:
            member_count = User.objects.count_faculty_members(faculty)

            faculty_list.append({
                'faculty_pk': faculty.pk,
                'faculty_name': faculty.faculty_name,
                'member_count': member_count,

            })

        context = {
            'faculty_list': faculty_list,
        }

        return render(request, self.template_name, context)


class CreateDepartment(LoginRequiredMixin, TemplateView):
    template_name = 'schools/create-department.html'

    def get(self, request, *args, **kwargs):

        faculty_pk = kwargs.get('pk')

        new_department_form = NewDepartmentForm()

        if faculty_pk is not None:
            faculty = Faculty.objects.get_faculty(faculty_pk)
            new_department_form.set_initial(faculty.faculty_name)
            card_title = 'Edit Department'
        else:
            card_title = 'Create Department'

        context = {
            'new_department_form': new_department_form,
            'card_title': card_title
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        faculty_pk = kwargs.get('pk')
        if 'save_faculty' in request.POST:



            new_department_form = NewDepartmentForm(request.POST)

            if new_department_form.is_valid():
                faculty_name = new_department_form.clean_faculty()

                if faculty_pk is None:
                    faculty = Faculty.objects.create_faculty(faculty_name, request.user)
                    faculty_pk = faculty.pk
                else:
                    faculty = Faculty.objects.get_faculty(faculty_pk)
                    Faculty.objects.update_faculty_name(faculty, faculty_name)

        return HttpResponseRedirect(reverse('schools:view-department', args=(faculty_pk,)))

class ViewDepartment(LoginRequiredMixin, TemplateView):
    template_name = 'schools/view-department.html'

    def get(self, request, *args, **kwargs):

        faculty_pk = kwargs.get('pk')
        faculty = Faculty.objects.get_faculty(faculty_pk)

        faculty_member_list = User.objects.get_faculty_members(faculty)
        print(faculty_member_list)

        context = {
            'faculty_member_list': faculty_member_list,
            'faculty': faculty,
            'program_name': settings.PROGRAM_NAME
        }

        return render(request, self.template_name, context)

class DeleteDepartment(LoginRequiredMixin, DeleteView):

    model = Faculty

    def get_success_url(self):
        return reverse_lazy('schools:manage-departments')

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('schools:manage-departments'))
        else:
            return super(DeleteDepartment, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DeleteDepartment, self).get_context_data(**kwargs)
        context['faculty_pk'] = self.kwargs['pk']
        return context

class DeleteDepartmentUser(LoginRequiredMixin, DeleteView):

    model = User

    def get_success_url(self):
        faculty_pk = self.kwargs.get('faculty_pk')
        return reverse_lazy('schools:view-department', args=(faculty_pk,))

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            faculty_pk = kwargs.get('faculty_pk')
            return HttpResponseRedirect(reverse('schools:view-department', args=(faculty_pk,)))
        else:
            return super(DeleteDepartmentUser, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DeleteDepartmentUser, self).get_context_data(**kwargs)
        context['user_pk'] = self.kwargs['pk']
        context['faculty_pk'] = self.kwargs['faculty_pk']
        return context


class UserChangeDepartment(LoginRequiredMixin, TemplateView):
    template_name = 'schools/change-department.html'

    def get(self, request, *args, **kwargs):

        user = request.user
        user_faculties = user.get_user_department_membership()

        department_form = DepartmentForm()
        department_form.set_queryset(user_faculties)
        department_form.set_initial(user.faculty)

        context = {
            'department_form': department_form
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        if 'save' in request.POST:
            user = request.user
            department_form = DepartmentForm(request.POST)

            if department_form.is_valid():
                faculty = department_form.clean_faculty()
                user.faculty = faculty
                user.save()

        return redirect('core_nav:settings')

class UserEditDepartments(LoginRequiredMixin, TemplateView):
    template_name = 'schools/edit-user-departments.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        user_faculties = user.get_user_department_membership()

        context = {
            'user_faculties': user_faculties,
            'current_user_faculty': user.faculty
        }

        return render(request, self.template_name, context)


class UserJoinDepartment(LoginRequiredMixin, TemplateView):
    template_name = 'schools/user-join-department.html'

    def get(self, request, *args, **kwargs):

        department_form = DepartmentForm()
        school_faculties = Faculty.objects.get_school_faculties_non_member(request.user)
        department_form.set_queryset(school_faculties)

        context = {
            'department_form': department_form
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        if 'save' in request.POST:

            user = request.user
            department_form = DepartmentForm(request.POST)

            if department_form.is_valid():
                faculty = department_form.clean_faculty()
                user.member_of_faculties.add(faculty)
                user.save()

                return redirect('schools:user-edit-departments')

            context = {
                'department_form': department_form
            }

            return render(request, self.template_name, context)

        return redirect('schools:user-edit-departments')


def user_leave_department(request, *args, **kwargs):
    faculty_pk = kwargs.get('faculty_pk')

    user = request.user

    faculty = Faculty.objects.get_faculty(faculty_pk)
    user.member_of_faculties.remove(faculty)


    user.save()

    return redirect('schools:user-edit-departments')


class AccountExpired(TemplateView):

    template_name = 'schools/account-expired.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)

class UploadSchoolBadge(LoginRequiredMixin, TemplateView):

    template_name = 'schools/upload-school-badge.html'

    def get(self, request, *args, **kwargs):
        current_user = request.user
        school_badge_url = common_helpers.get_school_badge_url(current_user.school)

        school_badge_form = SchoolBadgeForm()

        context = {
            'school_badge_url': school_badge_url,
            'school_badge_form': school_badge_form
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':

            current_user = request.user
            school = current_user.school
            school_badge_form = SchoolBadgeForm(request.POST, request.FILES)

            if school_badge_form.is_valid():
                cleaned_form = school_badge_form.cleaned_data
                school_badge = cleaned_form.get('school_badge')

                school.school_badge = school_badge
                school.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'), '/')
