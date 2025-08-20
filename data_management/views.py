from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, UpdateView, ListView, CreateView, DeleteView
from django.http import Http404, HttpResponse
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
import secrets
from django.contrib import messages
from django.db import transaction

from .forms import UserRegistrationForm, UserLoginForm, StudentForm, StaffStudentForm, StaffStudentCreateForm
from django.contrib.auth import authenticate, login, logout

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

        return redirect("profile")
    except Exception as e:
        logger.error(f"Dashboard view error - User: {request.user.username}, Error: {str(e)}", exc_info=True)
        raise


class StudentDataDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'dashboard/student_data/student_data_detail.html'
    context_object_name = 'student_data'

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch                                            to add logging."""
        user_info = get_user_info(request)
        logger.info(f"Student data detail view accessed - User: {user_info['username']}, IP: {user_info['ip']}")
        # Removed redirect so staff remain on profile page with summary
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """Get student data for the authenticated user unless staff (staff sees only basic user info)."""
        try:
            user = self.request.user
            if user.is_staff or user.groups.filter(name="data_management_staff").exists():
                logger.info("Student data detail skipped for staff user=%s", user.username)
                return None
            logger.info(f"Student data detail requested - User: {user.username}")
            student_data = self.model.objects.get(user=user)
            logger.info(f"Student data retrieved successfully - User: {user.username}")
            return student_data
        except self.model.DoesNotExist:
            logger.warning(f"Student data not found - User: {self.request.user.username}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving student data - User: {self.request.user.username}, Error: {str(e)}", exc_info=True)
            return None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        is_staff = user.is_staff or user.groups.filter(name="data_management_staff").exists()
        ctx['is_staff_view'] = is_staff
        ctx['basic_user'] = user if is_staff else None
        return ctx


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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'basic_fields': [
                'full_name','email','whatsapp_number','birth_place','birth_date','gender',
                'marital_status','citizenship_status','region_origin','parents_name','parents_phone'
            ],
            'academic_fields': [
                'institution','faculty','major','degree_level','semester_level','latest_grade','level'
            ],
            'identity_extra_fields': [
                'passport_number','nik','lapdik_number','arrival_date','school_origin','umdah_name','umdah_phone','home_name','home_location'
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
            'financial_fields': [
                'education_funding', 'scholarship_source', 'living_cost', 'monthly_income'
            ],
            'organization_field': 'organization_history',
            'photo_field': 'photo',
        })
        return ctx

    def form_valid(self, form):
        action = self.request.POST.get('action', 'save')
        # Capture previous values before save for change detection
        previous_values = {f: getattr(self.get_object(), f) for f in self.form_class.Meta.fields if hasattr(self.get_object(), f)}
        # Set draft status based on action prior to saving
        form.instance.is_draft = (action == 'save_draft')
        response = super().form_valid(form)
        if action in ['save','save_back','save_draft']:
            changed = []
            for f in self.form_class.Meta.fields:
                if not hasattr(self.object, f):
                    continue
                if previous_values.get(f) != getattr(self.object, f):
                    changed.append(f)
            if changed:
                audit_logger.log_profile_update(
                    request=self.request,
                    updated_fields=changed,
                    success=True,
                    errors=None
                )
                security_logger.log_data_modification(
                    request=self.request,
                    action="UPDATE" if not self.object.is_draft else "UPDATE_DRAFT",
                    model="Student",
                    record_id=str(self.object.pk),
                    success=True
                )
        return response


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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        creds = self.request.session.pop('new_student_credentials', None)
        if creds:
            ctx['new_student_credentials'] = creds
        reset_creds = self.request.session.pop('reset_student_credentials', None)
        if reset_creds:
            ctx['reset_student_credentials'] = reset_creds
        return ctx


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
                'marital_status','citizenship_status','region_origin','parents_name','parents_phone'
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

    def form_valid(self, form):
        action = self.request.POST.get('action', 'save')
        # Capture previous values before save for change detection
        previous_values = {f: getattr(self.get_object(), f) for f in self.form_class.Meta.fields if hasattr(self.get_object(), f)}
        # Set draft status based on action prior to saving
        form.instance.is_draft = (action == 'save_draft')
        response = super().form_valid(form)
        if action in ['save','save_back','save_draft']:
            changed = []
            for f in self.form_class.Meta.fields:
                if not hasattr(self.object, f):
                    continue
                if previous_values.get(f) != getattr(self.object, f):
                    changed.append(f)
            if changed:
                audit_logger.log_profile_update(
                    request=self.request,
                    updated_fields=changed,
                    success=True,
                    errors=None
                )
                security_logger.log_data_modification(
                    request=self.request,
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


class StaffStudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StaffStudentCreateForm
    template_name = 'dashboard/staff/staff_student_create_form.html'
    context_object_name = 'student'

    def dispatch(self, request, *args, **kwargs):
        logger.info("[StaffStudentCreateView] dispatch start user=%s path=%s", request.user.username, request.path)
        if not request.user.groups.filter(name="data_management_staff").exists():
            logger.warning("[StaffStudentCreateView] access denied user=%s not in staff group", request.user.username)
            security_logger.log_access_attempt(
                request=request,
                resource="Staff Student Create",
                granted=False,
                reason="User is not a staff member"
            )
            raise Http404()
        security_logger.log_access_attempt(
            request=request,
            resource="Staff Student Create",
            granted=True
        )
        logger.info("[StaffStudentCreateView] access granted user=%s", request.user.username)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'basic_fields': [
                'full_name','email','whatsapp_number','birth_place','birth_date','gender',
                'marital_status','citizenship_status','region_origin','parents_name','parents_phone'
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

    def form_valid(self, form):
        action = self.request.POST.get('action', 'save')
        logger.info(
            "[StaffStudentCreateView] form_valid start user=%s action=%s draft=%s incoming_fields=%s",
            self.request.user.username, action, (action == 'save_draft'), list(form.cleaned_data.keys())
        )
        form.instance.is_draft = (action == 'save_draft')
        try:
            with transaction.atomic():
                pending_student = form.instance
                User = get_user_model()
                base_username_source = pending_student.email.split('@')[0] if pending_student.email else pending_student.full_name.split()[0]
                base_username = slugify(base_username_source) or 'user'
                username = base_username
                i = 1
                while User.objects.filter(username=username).exists():
                    i += 1
                    username = f"{base_username}{i}"
                logger.info("[StaffStudentCreateView] generated username=%s base=%s", username, base_username)
                password_plain = get_random_string(12)
                parts = pending_student.full_name.split()
                first_name = parts[0][:30]
                last_name = ' '.join(parts[1:])[:150] if len(parts) > 1 else ''
                user = User(username=username, email=pending_student.email, first_name=first_name, last_name=last_name)
                user.set_password(password_plain)
                user.save()
                logger.info("[StaffStudentCreateView] user created id=%s email=%s", user.id, user.email)
                existing_student = Student.objects.filter(user=user).first()
                if existing_student:
                    logger.info("[StaffStudentCreateView] reusing signal-created student id=%s", existing_student.id)
                    updated_fields = []
                    for field in form.fields.keys():
                        if hasattr(existing_student, field) and field in form.cleaned_data:
                            old_val = getattr(existing_student, field)
                            new_val = form.cleaned_data[field]
                            if old_val != new_val:
                                updated_fields.append(field)
                                setattr(existing_student, field, new_val)
                    existing_student.is_draft = pending_student.is_draft
                    existing_student.save()
                    logger.info("[StaffStudentCreateView] student updated id=%s changed_fields=%s", existing_student.id, updated_fields)
                    self.object = existing_student
                else:
                    logger.warning("[StaffStudentCreateView] no signal-created student found; using fallback creation path")
                    pending_student.user = user
                    response = super().form_valid(form)
                    self.object = form.instance
                    logger.info("[StaffStudentCreateView] fallback student created id=%s", self.object.id)
                self.request.session['new_student_credentials'] = {
                    'username': user.username,
                    'password': password_plain,
                    'student_id': str(self.object.pk)
                }
                logger.info("[StaffStudentCreateView] credentials stored in session for student_id=%s", self.object.pk)
                if self.object.email:
                    try:
                        login_url = self.request.build_absolute_uri('/')
                        message = (
                            f"Halo {self.object.full_name},\n\n"
                            f"Akun Anda telah dibuat di sistem KMM Mesir.\n\n"
                            f"Username: {user.username}\nPassword: {password_plain}\n\n"
                            f"Silakan login di: {login_url}\nSegera ganti password setelah login.\n\n"
                            f"Terima kasih."
                        )
                        send_mail(
                            subject='Akun KMM Mesir Anda',
                            message=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[self.object.email],
                            fail_silently=True
                        )
                        logger.info("[StaffStudentCreateView] credential email queued to %s", self.object.email)
                    except Exception as mail_exc:
                        logger.error("[StaffStudentCreateView] email send failure student_id=%s error=%s", self.object.pk, mail_exc, exc_info=True)
                security_logger.log_data_modification(
                    request=self.request,
                    action="CREATE",
                    model="User",
                    record_id=str(user.pk),
                    success=True
                )
                audit_logger.log_profile_update(
                    request=self.request,
                    updated_fields=list(form.cleaned_data.keys()),
                    success=True
                )
                security_logger.log_data_modification(
                    request=self.request,
                    action="CREATE_DRAFT" if self.object.is_draft else "CREATE",
                    model="Student",
                    record_id=str(self.object.id),
                    success=True
                )
            if existing_student:
                target_url = self.get_success_url()
                logger.info("[StaffStudentCreateView] redirecting (reuse path) student_id=%s to %s", self.object.pk, target_url)
                return redirect(target_url)
            logger.info("[StaffStudentCreateView] redirecting (fallback path) student_id=%s", self.object.pk)
            return response
        except Exception as e:
            logger.error("[StaffStudentCreateView] form_valid exception user=%s error=%s", self.request.user.username, e, exc_info=True)
            audit_logger.log_profile_update(
                request=self.request,
                updated_fields=list(getattr(form, 'cleaned_data', {}).keys()),
                success=False,
                errors={'general': str(e)}
            )
            raise

    def get_success_url(self):
        action = self.request.POST.get('action') or self.request.GET.get('action')
        if action == 'save_back':
            url = self.request.POST.get('next') or self.request.GET.get('next') or reverse_lazy('staff_student_list')
            logger.info("[StaffStudentCreateView] get_success_url action=save_back url=%s", url)
            return url
        if action == 'save_draft':
            url = reverse_lazy('staff_student_edit', kwargs={'pk': self.object.pk})
            logger.info("[StaffStudentCreateView] get_success_url action=save_draft url=%s", url)
            return url
        next_param = self.request.GET.get('next') or self.request.POST.get('next')
        if next_param:
            logger.info("[StaffStudentCreateView] get_success_url next_param=%s", next_param)
            return next_param
        url = reverse_lazy('staff_student_detail', kwargs={'pk': self.object.pk})
        logger.info("[StaffStudentCreateView] get_success_url default detail url=%s", url)
        return url


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

# Password reset for a student (staff action)
@login_required
def staff_student_reset_password(request, pk):
    if request.method != 'POST':
        raise Http404()
    if not request.user.groups.filter(name="data_management_staff").exists():
        raise Http404()
    student = get_object_or_404(Student, pk=pk)
    if not student.user:
        raise Http404()
    user = student.user
    # Generate new secure password
    new_password = secrets.token_urlsafe(10)
    user.set_password(new_password)
    user.save()
    # Store one-time display
    request.session['reset_student_credentials'] = {
        'username': user.username,
        'password': new_password,
        'student_id': str(student.pk)
    }
    # Email the new password
    if student.email:
        try:
            message = (
                f"Halo {student.full_name},\n\nPassword akun Anda telah direset oleh staff.\n\n"
                f"Username: {user.username}\nPassword baru: {new_password}\n\n"
                f"Segera login dan ganti password ini demi keamanan.\n\nTerima kasih."
            )
            send_mail(
                subject='Reset Password Akun KMM Mesir',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=True
            )
        except Exception:
            pass
    security_logger.log_data_modification(
        request=request,
        action="UPDATE",
        model="User",
        record_id=str(user.pk),
        success=True
    )
    return redirect('staff_student_detail', pk=student.pk)

class StaffStudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'dashboard/staff/staff_student_confirm_delete.html'
    context_object_name = 'student'
    success_url = reverse_lazy('staff_student_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="data_management_staff").exists():
            security_logger.log_access_attempt(
                request=request,
                resource="Staff Student Delete",
                granted=False,
                reason="User is not a staff member"
            )
            raise Http404()
        security_logger.log_access_attempt(
            request=request,
            resource="Staff Student Delete",
            granted=True
        )
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        student_id = str(self.object.pk)
        student_name = self.object.full_name
        response = super().delete(request, *args, **kwargs)
        security_logger.log_data_modification(
            request=request,
            action="DELETE",
            model="Student",
            record_id=student_id,
            success=True
        )
        messages.success(request, f"Data mahasiswa '{student_name}' berhasil dihapus.")
        return response


def user_logout(request):
    """Unified logout for student or staff, with security logging and proper redirect.
    Only accepts POST for safety.
    Adds success flash message after logout.
    """
    if request.method != 'POST':
        return redirect('dashboard') if request.user.is_authenticated else redirect('login')
    was_staff = False
    if request.user.is_authenticated:
        was_staff = request.user.is_staff or request.user.groups.filter(name="data_management_staff").exists()
        security_logger.log_logout(request)
    logout(request)
    # Add success message on new (clean) session after logout
    messages.success(request, 'Berhasil logout.')
    return redirect('staff_login' if was_staff else 'login')
