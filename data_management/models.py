import uuid

from django.contrib.auth import get_user_model
from django.db import models


class Student(models.Model):
    DEGREE_LEVEL_CHOICES = [
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

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='student_profile')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    passport_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nik = models.CharField(max_length=16, unique=True, null=True, blank=True)
    lapdik_number = models.CharField(max_length=30, blank=True)
    birth_place = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    arrival_date = models.DateField(null=True, blank=True)
    school_origin = models.CharField(max_length=120, blank=True)
    citizenship_status = models.CharField(max_length=50, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, db_index=True)
    region_origin = models.CharField(max_length=80, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    institution = models.CharField(max_length=120, blank=True)
    faculty = models.CharField(max_length=120, blank=True)
    major = models.CharField(max_length=120, blank=True)
    degree_level = models.CharField(max_length=20, choices=DEGREE_LEVEL_CHOICES, db_index=True)
    semester_level = models.SmallIntegerField()
    latest_grade = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    home_name = models.CharField(max_length=80, blank=True)
    home_location = models.CharField(max_length=150, blank=True)
    parents_name = models.CharField(max_length=150, blank=True)
    parents_phone = models.CharField(max_length=20, blank=True, verbose_name="Nomor Telepon Orang Tua")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='maba', db_index=True)
    is_draft = models.BooleanField(default=False)  # indicates incomplete / draft record managed by staff

    # Health Information
    DISEASE_STATUS_CHOICES = [
        ('sembuh', 'Sembuh'),
        ('belum', 'Belum Sembuh'),
    ]
    disease_history = models.CharField(max_length=255, blank=True, verbose_name="Riwayat Penyakit")
    disease_status = models.CharField(max_length=10, choices=DISEASE_STATUS_CHOICES, blank=True)

    # Interests and Talents
    sport_interest = models.CharField(max_length=150, blank=True, verbose_name="Minat Olahraga")
    sport_achievement = models.TextField(blank=True, verbose_name="Prestasi Olahraga")
    art_interest = models.CharField(max_length=150, blank=True, verbose_name="Minat Kesenian")
    art_achievement = models.TextField(blank=True, verbose_name="Prestasi Kesenian")
    literacy_interest = models.CharField(max_length=150, blank=True, verbose_name="Minat Literasi")
    literacy_achievement = models.TextField(blank=True, verbose_name="Prestasi Literasi")
    science_interest = models.CharField(max_length=150, blank=True, verbose_name="Minat Keilmuan")
    science_achievement = models.TextField(blank=True, verbose_name="Prestasi Keilmuan")
    mtq_interest = models.CharField(max_length=150, blank=True, verbose_name="Minat MTQ")
    mtq_achievement = models.TextField(blank=True, verbose_name="Prestasi MTQ")
    media_interest = models.CharField(max_length=150, blank=True, verbose_name="Minat Media")
    media_achievement = models.TextField(blank=True, verbose_name="Prestasi Media")

    # Organizational History
    organization_history = models.TextField(blank=True, verbose_name="Riwayat Organisasi")

    # Financial Information
    education_funding = models.CharField(
        max_length=20,
        choices=EDUCATION_FUNDING_CHOICES,
        blank=True,
        verbose_name="Sumber Pendanaan Pendidikan"
    )
    scholarship_source = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Sumber Beasiswa"
    )
    living_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Biaya Hidup Bulanan"
    )
    monthly_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Pendapatan Bulanan"
    )

    # Guardian Information (Wali)
    photo_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="Link Foto (Google Drive)"
    )
    guardian_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nama Wali/Umdah"
    )
    guardian_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Nomor HP Wali/Umdah"
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.semester_level < 1 or self.semester_level > 14:
            raise ValidationError({'semester_level': 'Semester level must be between 1 and 14.'})

        # Optionally, add phone number validation here

    @property
    def email(self):
        """Get email from related user model"""
        return self.user.email if self.user else ''

    @property
    def full_name(self):
        """Get full name from related user model"""
        if self.user:
            full = f"{self.user.first_name} {self.user.last_name}".strip()
            return full or self.user.username
        return ''

    def __str__(self):
        return self.full_name
