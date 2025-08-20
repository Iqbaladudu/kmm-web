from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion
from django.utils.text import slugify
from django.utils.crypto import get_random_string

def assign_users(apps, schema_editor):
    Student = apps.get_model('data_management', 'Student')
    app_label, model_name = settings.AUTH_USER_MODEL.split('.')
    User = apps.get_model(app_label, model_name)

    for student in Student.objects.filter(user__isnull=True):
        user = None
        # Try existing user by email if available and not already linked
        if student.email:
            existing = User.objects.filter(email=student.email).first()
            if existing and not hasattr(existing, 'student_profile'):
                user = existing
        base_source = (student.email.split('@')[0] if student.email else (student.full_name.split()[0] if student.full_name else 'user'))
        base = slugify(base_source) or 'user'
        username = base
        i = 1
        while User.objects.filter(username=username).exists():
            i += 1
            username = f"{base}{i}"
        if not user:
            pwd = get_random_string(12)
            parts = student.full_name.split() if student.full_name else []
            first = parts[0][:30] if parts else ''
            last = ' '.join(parts[1:])[:150] if len(parts) > 1 else ''
            user = User(username=username, email=student.email, first_name=first, last_name=last)
            user.set_password(pwd)
            user.save()
        student.user = user
        student.save(update_fields=['user'])

def reverse_assign_users(apps, schema_editor):
    # No-op reverse; we do not want to null user links after enforcing constraint
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0012_student_is_draft'),
    ]

    operations = [
        migrations.RunPython(assign_users, reverse_assign_users),
        migrations.AlterField(
            model_name='student',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]

