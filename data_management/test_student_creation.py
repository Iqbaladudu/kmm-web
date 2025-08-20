from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Student

class StudentCreationReuseSignalTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff_group, _ = Group.objects.get_or_create(name="data_management_staff")
        self.staff_user = User.objects.create_user(
            username='staff', email='staff@example.com', password='pass12345', is_staff=True
        )
        self.staff_user.groups.add(self.staff_group)
        self.client.login(username='staff', password='pass12345')

    def test_staff_create_student_reuses_signal_created_student(self):
        url = reverse('staff_student_create')
        payload = {
            'full_name': 'Alice Smith',
            'email': 'alice@example.com',
            'whatsapp_number': '',
            'birth_place': '',
            'birth_date': '',
            'gender': 'F',
            'marital_status': 'single',
            'citizenship_status': '',
            'region_origin': '',
            'parents_name': '',
            'institution': '',
            'faculty': '',
            'major': '',
            'degree_level': 'S2',
            'semester_level': 3,
            'latest_grade': '',
            'passport_number': '',
            'nik': '',
            'lapdik_number': '',
            'arrival_date': '',
            'school_origin': '',
            'home_name': '',
            'home_location': '',
            'level': 'maba',
            'disease_history': '',
            'disease_status': '',
            'sport_interest': '',
            'sport_achievement': '',
            'art_interest': '',
            'art_achievement': '',
            'literacy_interest': '',
            'literacy_achievement': '',
            'science_interest': '',
            'science_achievement': '',
            'mtq_interest': '',
            'mtq_achievement': '',
            'media_interest': '',
            'media_achievement': '',
            'organization_history': '',
            'is_draft': '',
            'action': 'save'
        }
        pre_users = get_user_model().objects.count()
        resp = self.client.post(url, data=payload)
        self.assertIn(resp.status_code, (302, 303))
        self.assertEqual(get_user_model().objects.count(), pre_users + 1)
        qs = Student.objects.filter(email='alice@example.com')
        self.assertEqual(qs.count(), 1, 'Should have exactly one student linked to new user')
        s = qs.first()
        self.assertEqual(s.gender, 'F')
        self.assertEqual(s.degree_level, 'S2')
        self.assertEqual(s.semester_level, 3)

