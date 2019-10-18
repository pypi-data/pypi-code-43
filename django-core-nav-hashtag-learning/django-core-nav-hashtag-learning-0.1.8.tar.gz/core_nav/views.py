from common import common_helpers
from common.common_helpers import TRIAL_LENGTH
from config.settings.base import PROGRAM_NAME, PROGRAM_VERSION, PROGRAM_RELEASE_DATE, PROGRAM_DESCRIPTION_SCHOOL, \
    PROGRAM_DESCRIPTION_DEPARTMENTAL, LAUNCH_PAGE, FAQ_PAGE, ALERT_EMAIL_ADDRESSES
from core_nav.forms import UserDetailsForm, SchoolDetailsForm, ShowHelpForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import resolve
from django.urls import reverse
from django.views.generic import TemplateView
from help import overview_help_guides
from schools.models import School, Faculty
from users.models import User



class HomeView(LoginRequiredMixin, TemplateView):
    home_template_name = 'core_nav/home.html'
    welcome_template_name = 'core_nav/user-details.html'

    def get(self, request, *args, **kwargs):

        user = request.user

        if user.is_authenticated:

            if len(user.first_name) > 0:

                is_departmental = request.user.is_departmental()
                if is_departmental:
                    program_description = PROGRAM_DESCRIPTION_DEPARTMENTAL
                else:
                    program_description = PROGRAM_DESCRIPTION_SCHOOL

                context = {
                    'program_name': PROGRAM_NAME,
                    'program_description': program_description,
                    'launch_page': reverse(LAUNCH_PAGE),
                    'show_overview_help': user.show_overview_help
                }

                return render(request, self.home_template_name, context)
            else:

                user_details_form = UserDetailsForm()
                school_details_form = SchoolDetailsForm()

                context = {
                    'program_name': PROGRAM_NAME,
                    'user_details_form': user_details_form,
                    'school_details_form': school_details_form,

                }

                return render(request, self.welcome_template_name, context)


        else:
            return redirect('account_login')

    def post(self, request, *args, **kwargs):

        if 'save_name' in request.POST:

            user_details_form = UserDetailsForm(request.POST)

            if user_details_form.is_valid():
                request.user.first_name = user_details_form.clean_first_name()
                request.user.last_name = user_details_form.clean_last_name()
                request.user.save()

                if request.user.school is None:
                    return HttpResponseRedirect(reverse('core_nav:school-details'))
                else:
                    return HttpResponseRedirect(reverse('core_nav:get-started-invite'))

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class SchoolDetailsView(LoginRequiredMixin, TemplateView):
    template_name = 'core_nav/school-details.html'

    def get(self, request, *args, **kwargs):

        school_details_form = SchoolDetailsForm()

        context = {
            'program_name': PROGRAM_NAME,
            'school_details_form': school_details_form,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        if 'save_school' in request.POST:

            school_details_form = SchoolDetailsForm(request.POST)

            if school_details_form.is_valid():
                school_name = school_details_form.clean_school_name()
                authority = school_details_form.clean_authority()
                school_type = school_details_form.clean_school_type()

                school = School.objects.new_school_account(school_name, authority, school_type)
                request.user.school = school
                school_as_faculty = Faculty.objects.get_school_as_faculty()
                request.user.faculty = school_as_faculty
                request.user.save()

                msg = 'There is a new account sign up' + '\n\n'
                msg += "Program: " + PROGRAM_NAME + '\n'
                msg += 'School: ' + school_name + '\n'
                msg += 'Authority: ' + authority.authority_name + '\n'
                msg += 'School Type: ' + school_type + '\n\n'

                msg += 'User: ' + request.user.first_name + ' ' + request.user.last_name  + '\n'
                msg += 'Email: ' + request.user.email

                send_mail("New " + PROGRAM_NAME + " Sign Up", msg,
                          "Hashtag Learning<contact@hashtag-learning.co.uk>", ALERT_EMAIL_ADDRESSES)

                return HttpResponseRedirect(reverse('core_nav:get-started'))

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



class GetStarted(LoginRequiredMixin, TemplateView):
    template_name = 'core_nav/get-started.html'

    def get(self, request, *args, **kwargs):

        current_url = resolve(request.path_info).url_name
        if 'invite' in current_url:
            new_account = False
        else:
            new_account = True

        context = {
            'program_name': PROGRAM_NAME,
            'trial_length': TRIAL_LENGTH,
            'school_name': request.user.school.school_name,
            'new_account': new_account
        }

        return render(request, self.template_name, context)


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'core_nav/settings.html'

    def get(self, request, *args, **kwargs):
        current_user = request.user

        user_department_membership_count = current_user.count_user_department_membership()
        can_upload_badge = common_helpers.can_upload_badge()
        school_badge_url = common_helpers.get_school_badge_url(current_user.school)

        context = {
            'program_name': PROGRAM_NAME,
            'faq_page': FAQ_PAGE,
            'current_user': current_user,
            'user_department_membership_count': user_department_membership_count,
            'can_upload_badge': can_upload_badge,
            'school_badge_url': school_badge_url
        }

        return render(request, self.template_name, context)


class AboutView(LoginRequiredMixin, TemplateView):

    template_name = 'core_nav/about.html'

    def get(self, request, *args, **kwargs):

        context = {
            'program_name': PROGRAM_NAME,
            'program_version': PROGRAM_VERSION,
            'program_release_date': PROGRAM_RELEASE_DATE
        }

        return render(request, self.template_name, context)


class OverviewHelp(LoginRequiredMixin, TemplateView):
    template_name = 'core_nav/overview-help.html'

    def get(self, request, *args, **kwargs):

        show_help_form = ShowHelpForm()
        show_help_form.set_initial()

        help_pages = overview_help_guides.get_help_text()

        paginator = Paginator(help_pages, 1)
        page = request.GET.get('page')
        paginated_pages = paginator.get_page(page)

        context = {
            'program_name': PROGRAM_NAME,
            'show_help_form': show_help_form,
            'help_pages': help_pages,
            'paginated_pages': paginated_pages,
            'paginator': paginator
        }



        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        if 'done' in request.POST:
            show_help_form = ShowHelpForm(request.POST)
            if show_help_form.is_valid():
                dont_show_help = show_help_form.clean_dont_show_help()
                User.objects.update_dont_show_help(dont_show_help, request.user)

        return HttpResponseRedirect(reverse(LAUNCH_PAGE))
