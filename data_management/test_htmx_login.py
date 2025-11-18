"""
Test HTMX Login Functionality
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class HTMXLoginTestCase(TestCase):
    """Test cases for HTMX-enhanced login views"""

    def setUp(self):
        """Set up test users"""
        self.client = Client()
        User = get_user_model()

        # Create regular user
        self.regular_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )

        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='staffpass123',
            email='staff@example.com',
            first_name='Staff',
            last_name='User',
            is_staff=True
        )

    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(reverse('data_management:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'login-form-container')

    def test_staff_login_page_loads(self):
        """Test that staff login page loads successfully"""
        response = self.client.get(reverse('data_management:staff_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_login.html')
        self.assertContains(response, 'staff-login-form-container')

    def test_regular_login_success(self):
        """Test successful regular user login"""
        response = self.client.post(
            reverse('data_management:login'),
            {
                'username': 'testuser',
                'password': 'testpass123'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_regular_login_htmx_success(self):
        """Test successful regular user login via HTMX"""
        response = self.client.post(
            reverse('data_management:login'),
            {
                'username': 'testuser',
                'password': 'testpass123'
            },
            HTTP_HX_REQUEST='true'
        )
        # Should return HX-Redirect header
        self.assertIn('HX-Redirect', response.headers)

    def test_regular_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(
            reverse('data_management:login'),
            {
                'username': 'testuser',
                'password': 'wrongpassword'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, 'salah')  # Indonesian error message

    def test_regular_login_htmx_invalid_credentials(self):
        """Test login with invalid credentials via HTMX"""
        response = self.client.post(
            reverse('data_management:login'),
            {
                'username': 'testuser',
                'password': 'wrongpassword'
            },
            HTTP_HX_REQUEST='true'
        )
        # Should return partial template with errors
        self.assertTemplateUsed(response, 'partials/login_form.html')
        self.assertContains(response, 'salah')

    def test_staff_login_success(self):
        """Test successful staff login"""
        response = self.client.post(
            reverse('data_management:staff_login'),
            {
                'username': 'staffuser',
                'password': 'staffpass123'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTrue(response.wsgi_request.user.is_staff)

    def test_staff_login_htmx_success(self):
        """Test successful staff login via HTMX"""
        response = self.client.post(
            reverse('data_management:staff_login'),
            {
                'username': 'staffuser',
                'password': 'staffpass123'
            },
            HTTP_HX_REQUEST='true'
        )
        # Should return HX-Redirect header
        self.assertIn('HX-Redirect', response.headers)

    def test_staff_login_non_staff_user(self):
        """Test staff login with non-staff user"""
        response = self.client.post(
            reverse('data_management:staff_login'),
            {
                'username': 'testuser',
                'password': 'testpass123'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, 'staff')

    def test_staff_login_htmx_non_staff_user(self):
        """Test staff login with non-staff user via HTMX"""
        response = self.client.post(
            reverse('data_management:staff_login'),
            {
                'username': 'testuser',
                'password': 'testpass123'
            },
            HTTP_HX_REQUEST='true'
        )
        # Should return partial template with errors
        self.assertTemplateUsed(response, 'partials/staff_login_form.html')
        self.assertContains(response, 'staff')

    def test_htmx_header_detection(self):
        """Test that HTMX requests are properly detected"""
        # Without HTMX header
        response = self.client.post(
            reverse('data_management:login'),
            {
                'username': 'wronguser',
                'password': 'wrongpass'
            }
        )
        self.assertTemplateUsed(response, 'login.html')

        # With HTMX header
        response = self.client.post(
            reverse('data_management:login'),
            {
                'username': 'wronguser',
                'password': 'wrongpass'
            },
            HTTP_HX_REQUEST='true'
        )
        self.assertTemplateUsed(response, 'partials/login_form.html')

    def test_login_form_contains_htmx_attributes(self):
        """Test that login form contains proper HTMX attributes"""
        response = self.client.get(reverse('data_management:login'))
        self.assertContains(response, 'hx-post')
        self.assertContains(response, 'hx-target')
        self.assertContains(response, 'hx-swap')
        self.assertContains(response, 'hx-indicator')

    def test_staff_login_form_contains_htmx_attributes(self):
        """Test that staff login form contains proper HTMX attributes"""
        response = self.client.get(reverse('data_management:staff_login'))
        self.assertContains(response, 'hx-post')
        self.assertContains(response, 'hx-target')
        self.assertContains(response, 'hx-swap')
        self.assertContains(response, 'hx-indicator')

