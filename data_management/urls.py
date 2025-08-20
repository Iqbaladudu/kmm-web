from django.urls import path
from . import views

app_name = 'data_management'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('staff/', views.staff_login, name='staff_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("dashboard/profile/", views.StudentDataDetailView.as_view(), name='profile'),
    path("dashboard/profile/edit/", views.StudentDataUpdateView.as_view(), name='profile_edit'),
    path('dashboard/staff/students/', views.StaffDashboardDataListView.as_view(), name='staff_student_list'),
    path('dashboard/staff/students/add/', views.StaffStudentCreateView.as_view(), name='staff_student_create'),
    path('dashboard/staff/students/<uuid:pk>/', views.StaffStudentDetailView.as_view(), name='staff_student_detail'),
    path('dashboard/staff/students/export/csv/', views.export_students_csv, name='export_students_csv'),
    path('dashboard/staff/students/<uuid:pk>/edit/', views.StaffStudentUpdateView.as_view(), name='staff_student_edit'),
    path('dashboard/staff/students/<uuid:pk>/reset-password/', views.staff_student_reset_password, name='staff_student_reset_password'),
    path('dashboard/staff/students/<uuid:pk>/delete/', views.StaffStudentDeleteView.as_view(), name='staff_student_delete'),
]
