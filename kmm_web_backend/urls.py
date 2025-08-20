"""
URL configuration for kmm_web_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from data_management.health_checks import HealthCheckView, ReadinessCheckView, LivenessCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('data_management.urls')),
]

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]

# Add health check URLs at the end of urlpatterns
urlpatterns += [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('ready/', ReadinessCheckView.as_view(), name='readiness_check'),
    path('alive/', LivenessCheckView.as_view(), name='liveness_check'),
]
