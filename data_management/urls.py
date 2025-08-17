from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.user_login, name='login'),
    path('staff/', views.staff_login, name='staff_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("dashboard/profile/", views.StudentDataDetailView.as_view(), name='profile'),
    path("dashboard/profile/edit/", views.StudentDataUpdateView.as_view(), name='profile_edit'),
    path('dashboard/staff/students/', views.StaffDashboardDataListView.as_view(), name='staff_student_list'),
    path('dashboard/staff/students/<uuid:pk>/', views.StaffStudentDetailView.as_view(), name='staff_student_detail'),
    path('dashboard/staff/students/export/csv/', views.export_students_csv, name='export_students_csv'),
    path('dashboard/staff/students/<uuid:pk>/edit/', views.StaffStudentUpdateView.as_view(), name='staff_student_edit'),
]
