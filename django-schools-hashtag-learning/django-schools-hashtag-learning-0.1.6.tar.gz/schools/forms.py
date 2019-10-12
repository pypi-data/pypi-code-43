from allauth.account.forms import SignupForm
from django.forms import Form, CharField, ModelForm

from schools.models import School, Faculty
from users.models import User


class InviteUserForm(Form):
    email = CharField(max_length=60)

    def __init__(self, *args, **kwargs):
        super(InviteUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'


class InvitationSignupForm(SignupForm):

    def __init__(self, *args, **kwargs):
        super(InvitationSignupForm, self).__init__(*args, **kwargs)

    def save(self, request):
        user = super(InvitationSignupForm, self).save(request)
        school = School.objects.get(pk=self.school_id)
        user.school = school
        school_as_faculty = Faculty.objects.get_school_as_faculty()
        user.faculty = school_as_faculty
        user.save()
        return user


class DepartmentInvitationSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(DepartmentInvitationSignupForm, self).__init__(*args, **kwargs)

    def save(self, request):
        user = super(DepartmentInvitationSignupForm, self).save(request)
        faculty = Faculty.objects.get(pk=self.faculty_id)
        user.school = faculty.owner
        user.faculty = faculty
        user.school_admin=False
        user.member_of_faculties.add(faculty)
        user.save()
        return user

# Create a new user defined faculty
class NewDepartmentForm(ModelForm):

    class Meta:
        model = Faculty
        fields = ('faculty_name',)

    def __init__(self, *args, **kwargs):
        super(NewDepartmentForm, self).__init__(*args, **kwargs)
        self.fields['faculty_name'].widget.attrs['class'] = 'form-control'
        self.fields['faculty_name'].widget.attrs['placeholder'] = 'Department Name...'

    def set_initial(self, faculty_name):
        self.fields['faculty_name'].initial = faculty_name

    def clean_faculty(self):
        faculty_name = self.cleaned_data.get('faculty_name')
        return faculty_name


class DepartmentForm(ModelForm):

    class Meta:
        model = User
        fields = ('faculty',)

    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)
        self.fields['faculty'].widget.attrs['class'] = 'form-control'
        self.fields['faculty'].empty_label = None

    def set_queryset(self, school_faculties):
        self.fields['faculty'].queryset = school_faculties

    def set_initial(self, current_faculty):
        self.fields['faculty'].initial = current_faculty

    def clean_faculty(self):
        return self.cleaned_data.get('faculty')


class SchoolBadgeForm(ModelForm):
    class Meta:
        model = School
        fields = ['school_badge']
