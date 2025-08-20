from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import Group

class AuthRedirectMiddlewareTest(TestCase):
    def setUp(self):
        User = get_user_model()
        # Regular student user (signal will create Student)
        self.student = User.objects.create_user(
            username='studx', email='studx@example.com', password='pass12345'
        )
        # Staff user
        self.staff = User.objects.create_user(
            username='staffx', email='staffx@example.com', password='pass12345', is_staff=True
        )
        # Ensure group exists for completeness
        self.staff_group, _ = Group.objects.get_or_create(name='data_management_staff')
        self.staff.groups.add(self.staff_group)

    def test_student_redirect_root(self):
        self.client.login(username='studx', password='pass12345')
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard/profile/', resp.url)

    def test_student_redirect_staff_login_page(self):
        self.client.login(username='studx', password='pass12345')
        resp = self.client.get('/staff/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard/profile/', resp.url)

    def test_student_redirect_register_page(self):
        self.client.login(username='studx', password='pass12345')
        resp = self.client.get('/register/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard/profile/', resp.url)

    def test_staff_redirect_root(self):
        self.client.login(username='staffx', password='pass12345')
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard/', resp.url)

    def test_staff_redirect_staff_login_page(self):
        self.client.login(username='staffx', password='pass12345')
        resp = self.client.get('/staff/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard/', resp.url)

    def test_staff_redirect_register_page(self):
        self.client.login(username='staffx', password='pass12345')
        resp = self.client.get('/register/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard/', resp.url)

    def test_head_request(self):
        self.client.login(username='staffx', password='pass12345')
        resp = self.client.head('/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard/', resp.url)

    def test_anonymous_no_redirect(self):
        resp = self.client.get('/')
        # Should display login page (200) not redirect for anonymous
        self.assertEqual(resp.status_code, 200)
        resp_staff = self.client.get('/staff/')
        self.assertEqual(resp_staff.status_code, 200)
        resp_register = self.client.get('/register/')
        self.assertEqual(resp_register.status_code, 200)
