from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, UpdateView
from django.http import Http404
from django.urls import reverse_lazy

from .forms import UserRegistrationForm, UserLoginForm, StudentForm
from django.contrib.auth import authenticate, login

from .models import Student
import logging

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    logger.info(f"User {request.user.username} accessed the dashboard.")
    if request.user.groups.filter(name="data_management_staff").exists():
        logger.info(f"User {request.user.username} is a data management staff member.")
    return render(request, 'dashboard/dashboard.html')


class StudentDataDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'dashboard/student_data/student_data_detail.html'
    context_object_name = 'student_data'

    def get_object(self, queryset=None):
        try:
            return self.model.objects.get(user=self.request.user)
        except self.model.DoesNotExist:
            return None  # Return None instead of raising Http404


class StudentDataUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    template_name = 'dashboard/student_data/student_data_form.html'
    form_class = StudentForm
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, user=self.request.user)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optionally, you can log the user in after registration
            # from django.contrib.auth import login
            # login(request, user)
            return redirect('login')  # Redirect to a login page or home page
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard/profile')  # Change 'home' to your desired redirect
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def staff_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('dashboard')  # Redirect to the staff dashboard
            else:
                form.add_error(None, 'Invalid username or password or not a staff member')
    else:
        form = UserLoginForm()
    return render(request, 'staff_login.html', {'form': form})