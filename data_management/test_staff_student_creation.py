from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Student

class TestStaffStudentCreationFlow(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff_group, _ = Group.objects.get_or_create(name="data_management_staff")
        self.staff_user = User.objects.create_user(
            username='staffuser', email='staffuser@example.com', password='pass12345', is_staff=True
        )
        self.staff_user.groups.add(self.staff_group)
        logged_in = self.client.login(username='staffuser', password='pass12345')
        self.assertTrue(logged_in, 'Failed to log in test staff user')

    def test_staff_creates_student_reuses_signal_student(self):
        url = reverse('staff_student_create')
        payload = {
            'full_name': 'Bob Builder',
            'email': 'bob@example.com',
            'whatsapp_number': '',
            'birth_place': '',
            'birth_date': '',
            'gender': 'M',
            'marital_status': 'single',
            'citizenship_status': '',
            'region_origin': '',
            'parents_name': '',
            'institution': '',
            'faculty': '',
            'major': '',
            'degree_level': 'S3',
            'semester_level': 7,
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
        pre_user_count = get_user_model().objects.count()
        response = self.client.post(url, data=payload)
        # Redirect indicates success
        self.assertIn(response.status_code, (302, 303))
        self.assertEqual(get_user_model().objects.count(), pre_user_count + 1)
        students = Student.objects.filter(email='bob@example.com')
        self.assertEqual(students.count(), 1, 'Exactly one student should be created / reused')
        s = students.first()
        # Confirm updated values applied over signal defaults
        self.assertEqual(s.degree_level, 'S3')
        self.assertEqual(s.semester_level, 7)
        self.assertEqual(s.gender, 'M')

