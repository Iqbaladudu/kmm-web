from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class LogoutTest(TestCase):
    def setUp(self):
        User = get_user_model()
        # Regular user
        self.user = User.objects.create_user(username='student1', email='s1@example.com', password='pass12345')
        # Staff user
        self.staff_group, _ = Group.objects.get_or_create(name='data_management_staff')
        self.staff = User.objects.create_user(username='staff1', email='st1@example.com', password='pass12345', is_staff=True)
        self.staff.groups.add(self.staff_group)

    def test_student_logout_redirects_login(self):
        self.client.login(username='student1', password='pass12345')
        resp = self.client.post(reverse('logout'), follow=True)
        # Final URL should be login
        self.assertEqual(resp.resolver_match.view_name, 'login')
        # Check for data-autohide attribute in logout success message
        self.assertIn('data-autohide="true"', resp.content.decode())
        # Flash message present
        messages = list(resp.context['messages'])
        self.assertTrue(any('Berhasil logout.' in str(m) for m in messages))
        # After logout accessing protected should redirect to login
        profile_resp = self.client.get(reverse('profile'))
        self.assertEqual(profile_resp.status_code, 302)
        self.assertIn(reverse('login'), profile_resp.url)

    def test_staff_logout_redirects_staff_login(self):
        self.client.login(username='staff1', password='pass12345')
        resp = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(resp.resolver_match.view_name, 'staff_login')
        # Check for data-autohide attribute in logout success message
        self.assertIn('data-autohide="true"', resp.content.decode())
        messages = list(resp.context['messages'])
        self.assertTrue(any('Berhasil logout.' in str(m) for m in messages))
        dash_resp = self.client.get(reverse('dashboard'))
        self.assertEqual(dash_resp.status_code, 302)
        self.assertIn(reverse('login'), dash_resp.url)  # dashboard login redirect chain

    def test_logout_requires_post(self):
        self.client.login(username='student1', password='pass12345')
        resp = self.client.get(reverse('logout'))  # GET should not logout, redirected
        # Should redirect to dashboard/profile (user still logged in)
        self.assertEqual(resp.status_code, 302)
        # Confirm still authenticated by accessing profile
        profile_resp = self.client.get(reverse('profile'))
        self.assertEqual(profile_resp.status_code, 200)
        # Ensure no success message was set on GET request
        follow_resp = self.client.get(resp.url, follow=True)
        if 'messages' in follow_resp.context and follow_resp.context['messages']:
            self.assertFalse(any('Berhasil logout.' in str(m) for m in follow_resp.context['messages']))
