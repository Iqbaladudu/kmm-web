from django.contrib import admin
from .models import Student

class StudentAdmin(admin.ModelAdmin):

    list_display = ('full_name', 'email', 'level', 'faculty', 'major')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'passport_number', 'nik')
    list_filter = ('level', 'faculty', 'gender', 'region_origin')
    fieldsets = (
        ('Personal Info', {
            'fields': ('user', 'whatsapp_number', 'gender', 'birth_place', 'birth_date', 'marital_status', 'citizenship_status', 'region_origin')
        }),
        ('Academic Info', {
            'fields': ('level', 'institution', 'faculty', 'major', 'degree_level', 'semester_level', 'latest_grade', 'school_origin')
        }),
        ('Identity Info', {
            'fields': ('passport_number', 'nik', 'lapdik_number', 'arrival_date')
        }),
        ('Contact & Residence', {
            'fields': ('parents_name', 'home_name', 'home_location')
        }),
        ('Health Information', {
            'fields': ('disease_history', 'disease_status')
        }),
        ('Interests and Talents', {
            'fields': ('sport_interest', 'sport_achievement', 'art_interest', 'art_achievement', 'literacy_interest', 'literacy_achievement', 'science_interest', 'science_achievement', 'mtq_interest', 'mtq_achievement', 'media_interest', 'media_achievement')
        }),
        ('Organizational History', {
            'fields': ('organization_history',)
        }),
    )
    readonly_fields = ('id',)

# Register your models here.
admin.site.register(Student, StudentAdmin)
