# Generated manually to add financial fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0013_make_student_user_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='education_funding',
            field=models.CharField(
                blank=True,
                choices=[('beasiswa', 'Beasiswa'), ('non-beasiswa', 'Non-Beasiswa')],
                max_length=20,
                verbose_name='Sumber Pendanaan Pendidikan'
            ),
        ),
        migrations.AddField(
            model_name='student',
            name='scholarship_source',
            field=models.CharField(
                blank=True,
                max_length=150,
                verbose_name='Sumber Beasiswa'
            ),
        ),
        migrations.AddField(
            model_name='student',
            name='living_cost',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name='Biaya Hidup Bulanan'
            ),
        ),
        migrations.AddField(
            model_name='student',
            name='monthly_income',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name='Pendapatan Bulanan'
            ),
        ),
    ]
