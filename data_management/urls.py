from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.user_login, name='login'),
    path('staff/', views.staff_login, name='staff_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("dashboard/profile/", views.StudentDataDetailView.as_view(), name='profile'),
    path("dashboard/profile/edit/", views.StudentDataUpdateView.as_view(), name='profile_edit'),
]
