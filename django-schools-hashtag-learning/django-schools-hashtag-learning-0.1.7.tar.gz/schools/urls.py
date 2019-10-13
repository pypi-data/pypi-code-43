from django.urls import path
from . import views



app_name = 'schools'
urlpatterns = [
        path('invite-users/', views.InviteUsers.as_view(), name='invite-users'),
        path('<str:sent>/invite-users/', views.InviteUsers.as_view(), name='invite-users'),

    path('manage-departments/', views.ManageDepartments.as_view(), name='manage-departments'),
    path('create-department/', views.CreateDepartment.as_view(), name='create-department'),
    path('<int:pk>/edit-department/', views.CreateDepartment.as_view(), name='edit-department'),
    path('<int:pk>/view-department/', views.ViewDepartment.as_view(), name='view-department'),
    path('<int:pk>/delete-department/', views.DeleteDepartment.as_view(), name='delete-department'),
    path('<int:pk>/<int:faculty_pk>/delete-department-user/', views.DeleteDepartmentUser.as_view(), name='delete-department-user'),

    path('user-join-department/', views.UserJoinDepartment.as_view(), name='user-join-department'),
    path('<int:faculty_pk>/user-leave-department/', views.user_leave_department, name='user-leave-department'),
    path('user-change-department/', views.UserChangeDepartment.as_view(), name='user-change-department'),
    path('user-edit-departments/', views.UserEditDepartments.as_view(), name='user-edit-departments'),

    path('<int:pk>/invite-users-department/', views.InviteUsersDepartment.as_view(), name='invite-users-department'),

    path('account-expired/', views.AccountExpired.as_view(), name='account-expired'),

    path('schools:upload-school-badge/', views.UploadSchoolBadge.as_view(), name='upload-school-badge'),
        ]

