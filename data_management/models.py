import uuid
from django.db import models
from django.contrib.auth import get_user_model

class Student(models.Model):
    DEGREE_LEVEL_CHOICES = [
        ('D3', 'D3'),
        ('S1', 'S1'),
        ('S2', 'S2'),
        ('S3', 'S3'),
    ]
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
    ]
    EDUCATION_FUNDING_CHOICES = [
        ('beasiswa', 'Beasiswa'),
        ('non-beasiswa', 'Non-Beasiswa'),
    ]
    LEVEL_CHOICES = [
        ('maba', 'Mahasiswa Baru'),
        ('regular', 'Reguler'),
        ('alumni', 'Alumni'),
    ]

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=150)
    passport_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nik = models.CharField(max_length=16, unique=True, null=True, blank=True)
    lapdik_number = models.CharField(max_length=30, blank=True)
    birth_place = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    arrival_date = models.DateField(null=True, blank=True)
    school_origin = models.CharField(max_length=120, blank=True)
    citizenship_status = models.CharField(max_length=50, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES)
    region_origin = models.CharField(max_length=80, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=120, unique=True)
    institution = models.CharField(max_length=120, blank=True)
    faculty = models.CharField(max_length=120, blank=True)
    major = models.CharField(max_length=120, blank=True)
    degree_level = models.CharField(max_length=20, choices=DEGREE_LEVEL_CHOICES)
    semester_level = models.SmallIntegerField()
    latest_grade = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    home_name = models.CharField(max_length=80, blank=True)
    home_location = models.CharField(max_length=150, blank=True)
    parents_name = models.CharField(max_length=150, blank=True)
    parents_phone = models.CharField(max_length=20, blank=True)
    umdah_name = models.CharField(max_length=80, blank=True)
    umdah_phone = models.CharField(max_length=20, blank=True)
    education_funding = models.CharField(max_length=20, choices=EDUCATION_FUNDING_CHOICES)
    scholarship_source = models.CharField(max_length=120, null=True, blank=True)
    living_cost = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    photo = models.ImageField(upload_to='student_photos', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='regular')

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.semester_level < 1 or self.semester_level > 14:
            raise ValidationError({'semester_level': 'Semester level must be between 1 and 14.'})

        # Optionally, add phone number validation here

    def __str__(self):
        return self.full_name

