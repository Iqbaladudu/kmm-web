from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, UpdateView, ListView
from django.http import Http404, HttpResponse
from django.urls import reverse_lazy
from django.utils.http import urlencode

from .forms import UserRegistrationForm, UserLoginForm, StudentForm, StaffStudentForm
from django.contrib.auth import authenticate, login

from .models import Student
from .utils.logging_utils import security_logger, audit_logger, get_user_info, log_user_action
import logging
import csv

# Configure logger with proper naming convention
logger = logging.getLogger(__name__)

@login_required
@log_user_action('data_management.views')
def dashboard(request):
    """Dashboard view for authenticated users."""
    try:
        user_info = get_user_info(request)

        if request.user.groups.filter(name="data_management_staff").exists():
            logger.info(f"Staff member accessed dashboard - User: {user_info['username']}")
        else:
            logger.info(f"Regular user accessed dashboard - User: {user_info['username']}")

        return render(request, 'dashboard/dashboard.html')
    except Exception as e:
        logger.error(f"Dashboard view error - User: {request.user.username}, Error: {str(e)}", exc_info=True)
        raise


class StudentDataDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'dashboard/student_data/student_data_detail.html'
    context_object_name = 'student_data'

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to add logging."""
        user_info = get_user_info(request)
        logger.info(f"Student data detail view accessed - User: {user_info['username']}, IP: {user_info['ip']}")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """Get student data for the authenticated user."""
        try:
            logger.info(f"Student data detail requested - User: {self.request.user.username}")
            student_data = self.model.objects.get(user=self.request.user)
            logger.info(f"Student data retrieved successfully - User: {self.request.user.username}")
            return student_data
        except self.model.DoesNotExist:
            logger.warning(f"Student data not found - User: {self.request.user.username}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving student data - User: {self.request.user.username}, Error: {str(e)}", exc_info=True)
            return None


class StudentDataUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    template_name = 'dashboard/student_data/student_data_form.html'
    form_class = StudentForm
    success_url = reverse_lazy('profile')

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to add logging."""
        user_info = get_user_info(request)
        logger.info(f"Student data update view accessed - User: {user_info['username']}, IP: {user_info['ip']}")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """Get student object for update."""
        try:
            logger.info(f"Student data update requested - User: {self.request.user.username}")
            return get_object_or_404(self.model, user=self.request.user)
        except Exception as e:
            logger.error(f"Error getting student object for update - User: {self.request.user.username}, Error: {str(e)}", exc_info=True)
            raise

    def form_valid(self, form):
        """Handle valid form submission."""
        try:
            # Get changed fields for audit logging
            changed_fields = []
            if form.changed_data:
                changed_fields = form.changed_data

            response = super().form_valid(form)

            # Log successful update with audit trail
            audit_logger.log_profile_update(
                request=self.request,
                updated_fields=changed_fields,
                success=True
            )

            security_logger.log_data_modification(
                request=self.request,
                action="UPDATE",
                model="Student",
                record_id=str(self.object.id),
                success=True
            )

            return response
        except Exception as e:
            # Log failed update
            audit_logger.log_profile_update(
                request=self.request,
                updated_fields=form.changed_data if hasattr(form, 'changed_data') else [],
                success=False,
                errors={'general': str(e)}
            )

            logger.error(f"Error updating student data - User: {self.request.user.username}, Error: {str(e)}", exc_info=True)
            raise

    def form_invalid(self, form):
        """Handle invalid form submission."""
        # Log invalid form with audit trail
        audit_logger.log_profile_update(
            request=self.request,
            updated_fields=form.changed_data if hasattr(form, 'changed_data') else [],
            success=False,
            errors=dict(form.errors)
        )

        return super().form_invalid(form)


def register(request):
    """User registration view."""
    user_info = get_user_info(request)

    if request.method == 'POST':
        try:
            form = UserRegistrationForm(request.POST)

            if form.is_valid():
                user = form.save()
                username = user.username

                # Log successful registration
                audit_logger.log_user_registration(
                    request=request,
                    username=username,
                    success=True
                )

                security_logger.log_data_modification(
                    request=request,
                    action="CREATE",
                    model="User",
                    record_id=str(user.id),
                    success=True
                )

                return redirect('login')
            else:
                # Log failed registration
                audit_logger.log_user_registration(
                    request=request,
                    username=form.data.get('username', 'Unknown'),
                    success=False,
                    errors=dict(form.errors)
                )

        except Exception as e:
            logger.error(f"Registration error - IP: {user_info['ip']}, Error: {str(e)}", exc_info=True)
            # Re-initialize form on error
            form = UserRegistrationForm()
    else:
        logger.info(f"Registration page accessed from IP: {user_info['ip']}")
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def user_login(request):
    """User login view."""
    user_info = get_user_info(request)

    if request.method == 'POST':
        try:
            form = UserLoginForm(request.POST)

            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']

                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)

                    # Log successful login
                    security_logger.log_login_attempt(
                        request=request,
                        username=username,
                        success=True,
                        is_staff=False
                    )

                    return redirect('dashboard/profile')
                else:
                    # Log failed login
                    security_logger.log_login_attempt(
                        request=request,
                        username=username,
                        success=False,
                        is_staff=False,
                        additional_info="Invalid credentials"
                    )

                    form.add_error(None, 'Invalid username or password')
            else:
                logger.warning(f"Login failed - Invalid form data, IP: {user_info['ip']}, Errors: {form.errors}")

        except Exception as e:
            logger.error(f"Login error - IP: {user_info['ip']}, Error: {str(e)}", exc_info=True)
            form = UserLoginForm()
    else:
        logger.info(f"Login page accessed from IP: {user_info['ip']}")
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})


def staff_login(request):
    """Staff login view."""
    user_info = get_user_info(request)

    if request.method == 'POST':
        try:
            form = UserLoginForm(request.POST)

            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']

                user = authenticate(request, username=username, password=password)
                if user is not None and user.is_staff:
                    login(request, user)

                    # Log successful staff login
                    security_logger.log_login_attempt(
                        request=request,
                        username=username,
                        success=True,
                        is_staff=True
                    )

                    return redirect('dashboard')
                else:
                    if user is not None:
                        # Non-staff user attempted staff login
                        security_logger.log_login_attempt(
                            request=request,
                            username=username,
                            success=False,
                            is_staff=True,
                            additional_info="User is not staff member"
                        )
                    else:
                        # Invalid credentials
                        security_logger.log_login_attempt(
                            request=request,
                            username=username,
                            success=False,
                            is_staff=True,
                            additional_info="Invalid credentials"
                        )

                    form.add_error(None, 'Invalid username or password or not a staff member')
            else:
                logger.warning(f"Staff login failed - Invalid form data, IP: {user_info['ip']}, Errors: {form.errors}")

        except Exception as e:
            logger.error(f"Staff login error - IP: {user_info['ip']}, Error: {str(e)}", exc_info=True)
            form = UserLoginForm()
    else:
        logger.info(f"Staff login page accessed from IP: {user_info['ip']}")
        form = UserLoginForm()

    return render(request, 'staff_login.html', {'form': form})


class StaffDashboardDataListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'dashboard/staff/staff_dashboard_list.html'
    context_object_name = 'students'
    paginate_by = 10
    ordering = ['full_name']
    allowed_sort_fields = ['full_name', 'email', 'degree_level', 'semester_level', 'faculty', 'major', 'level']

    def dispatch(self, request, *args, **kwargs):
        # Permission check
        if not request.user.groups.filter(name="data_management_staff").exists():
            security_logger.log_access_attempt(
                request=request,
                resource="Staff Dashboard Data List",
                granted=False,
                reason="User is not a staff member"
            )
            raise Http404("You do not have permission to view this page.")
        security_logger.log_access_attempt(
            request=request,
            resource="Staff Dashboard Data List",
            granted=True
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset().select_related('user')
        q = self.request.GET.get('q', '').strip()
        gender = self.request.GET.get('gender', '').strip()
        degree_level = self.request.GET.get('degree_level', '').strip()
        level = self.request.GET.get('level', '').strip()
        marital_status = self.request.GET.get('marital_status', '').strip()
        sort = self.request.GET.get('sort', '').strip()
        direction = self.request.GET.get('dir', 'asc')

        from django.db.models import Q
        if q:
            qs = qs.filter(
                Q(full_name__icontains=q) |
                Q(email__icontains=q) |
                Q(passport_number__icontains=q) |
                Q(nik__icontains=q) |
                Q(faculty__icontains=q) |
                Q(major__icontains=q)
            )
        if gender:
            qs = qs.filter(gender=gender)
        if degree_level:
            qs = qs.filter(degree_level=degree_level)
        if level:
            qs = qs.filter(level=level)
        if marital_status:
            qs = qs.filter(marital_status=marital_status)
        if sort in self.allowed_sort_fields:
            ordering = f"{'-' if direction == 'desc' else ''}{sort}"
            qs = qs.order_by(ordering)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '')
        ctx['selected_gender'] = self.request.GET.get('gender', '')
        ctx['selected_degree_level'] = self.request.GET.get('degree_level', '')
        ctx['selected_level'] = self.request.GET.get('level', '')
        ctx['selected_marital_status'] = self.request.GET.get('marital_status', '')
        ctx['gender_choices'] = Student.GENDER_CHOICES
        ctx['degree_choices'] = Student.DEGREE_LEVEL_CHOICES
        ctx['level_choices'] = Student.LEVEL_CHOICES
        ctx['marital_choices'] = Student.MARITAL_STATUS_CHOICES
        ctx['current_sort'] = self.request.GET.get('sort', '')
        ctx['current_dir'] = self.request.GET.get('dir', 'asc')
        filter_params = {}
        for p in ['q','gender','degree_level','level','marital_status']:
            val = self.request.GET.get(p)
            if val:
                filter_params[p] = val
        ctx['base_filter_query'] = urlencode(filter_params)
        # Stats
        ctx['total_students'] = Student.objects.count()
        ctx['filtered_students'] = ctx['paginator'].count if 'paginator' in ctx else ctx['total_students']
        ctx['is_filtered'] = ctx['filtered_students'] != ctx['total_students']
        return ctx

class StaffStudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'dashboard/staff/staff_student_detail.html'
    context_object_name = 'student'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="data_management_staff").exists():
            security_logger.log_access_attempt(
                request=request,
                resource="Staff Student Detail",
                granted=False,
                reason="User is not a staff member"
            )
            raise Http404()
        return super().dispatch(request, *args, **kwargs)


class StaffStudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StaffStudentForm
    template_name = 'dashboard/staff/staff_student_form.html'
    context_object_name = 'student'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="data_management_staff").exists():
            security_logger.log_access_attempt(
                request=request,
                resource="Staff Student Edit",
                granted=False,
                reason="User is not a staff member"
            )
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'basic_fields': [
                'full_name','email','whatsapp_number','birth_place','birth_date','gender',
                'marital_status','citizenship_status','region_origin','parents_name'
            ],
            'academic_fields': [
                'institution','faculty','major','degree_level','semester_level','latest_grade','level'
            ],
            'identity_extra_fields': [
                'passport_number','nik','lapdik_number','arrival_date','school_origin','home_name','home_location'
            ],
            'health_fields': ['disease_history','disease_status'],
            'interest_field_pairs': [
                ('sport_interest','sport_achievement'),
                ('art_interest','art_achievement'),
                ('literacy_interest','literacy_achievement'),
                ('science_interest','science_achievement'),
                ('mtq_interest','mtq_achievement'),
                ('media_interest','media_achievement'),
            ],
            'organization_field': 'organization_history',
            'next_url': self.request.GET.get('next') or self.request.POST.get('next') or ''
        })
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        previous_values = {f: getattr(self.object, f) for f in self.form_class.Meta.fields if hasattr(self.object, f)}
        action = request.POST.get('action', 'save')
        # Adjust draft flag before form validation
        mutable_post = request.POST.copy()
        if action == 'save_draft':
            mutable_post['is_draft'] = 'on'
        else:
            # publishing clears draft flag
            mutable_post['is_draft'] = ''
        request.POST = mutable_post
        response = super().post(request, *args, **kwargs)
        if self.object and not isinstance(response, HttpResponse):
            # If form invalid, HttpResponse returned; skip logging changes
            return response
        if self.object and action in ['save','save_back','save_draft']:
            # Determine changed fields
            changed = []
            for f in self.form_class.Meta.fields:
                if not hasattr(self.object, f):
                    continue
                old = previous_values.get(f)
                new = getattr(self.object, f)
                if old != new:
                    changed.append(f)
            if changed:
                audit_logger.log_profile_update(
                    request=request,
                    updated_fields=changed,
                    success=True,
                    errors=None
                )
                security_logger.log_data_modification(
                    request=request,
                    action="UPDATE" if not self.object.is_draft else "UPDATE_DRAFT",
                    model="Student",
                    record_id=str(self.object.pk),
                    success=True
                )
        return response

    def get_success_url(self):
        action = self.request.POST.get('action') or self.request.GET.get('action')
        if action == 'save_back':
            return self.request.POST.get('next') or self.request.GET.get('next') or reverse_lazy('staff_student_list')
        # For draft remain on edit page
        if action == 'save_draft':
            return reverse_lazy('staff_student_edit', kwargs={'pk': self.object.pk})
        # Default behavior
        next_param = self.request.GET.get('next') or self.request.POST.get('next')
        if next_param:
            return next_param
        return reverse_lazy('staff_student_detail', kwargs={'pk': self.object.pk})


def export_students_csv(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name="data_management_staff").exists():
        raise Http404()
    # replicate filtering logic
    qs = Student.objects.all()
    q = request.GET.get('q', '').strip()
    gender = request.GET.get('gender', '').strip()
    degree_level = request.GET.get('degree_level', '').strip()
    level = request.GET.get('level', '').strip()
    marital_status = request.GET.get('marital_status', '').strip()

    from django.db.models import Q
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) |
            Q(email__icontains=q) |
            Q(passport_number__icontains=q) |
            Q(nik__icontains=q) |
            Q(faculty__icontains=q) |
            Q(major__icontains=q)
        )
    if gender:
        qs = qs.filter(gender=gender)
    if degree_level:
        qs = qs.filter(degree_level=degree_level)
    if level:
        qs = qs.filter(level=level)
    if marital_status:
        qs = qs.filter(marital_status=marital_status)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    writer = csv.writer(response)
    writer.writerow(['Full Name','Email','Passport','NIK','Degree','Semester','Faculty','Major','Level'])
    for s in qs.iterator():
        writer.writerow([
            s.full_name,
            s.email,
            s.passport_number or '',
            s.nik or '',
            s.degree_level,
            s.semester_level,
            s.faculty,
            s.major,
            s.get_level_display(),
        ])
    return response
