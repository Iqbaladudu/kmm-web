"""
Test password reset confirm functionality with HTMX support
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class PasswordResetConfirmTestCase(TestCase):
    """Test custom password reset confirm view with HTMX support"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='oldpassword123'
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = reverse('data_management:password_reset_confirm',
                           kwargs={'uidb64': self.uid, 'token': self.token})

    def test_password_reset_confirm_page_loads(self):
        """Test that password reset confirm page loads successfully"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_confirm.html')
        self.assertTrue(response.context['validlink'])
        self.assertIsNotNone(response.context['form'])

    def test_password_reset_confirm_invalid_link(self):
        """Test password reset with invalid token"""
        invalid_url = reverse('data_management:password_reset_confirm',
                              kwargs={'uidb64': self.uid, 'token': 'invalid-token'})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['validlink'])
        self.assertIsNone(response.context['form'])

    def test_password_reset_confirm_valid_submission(self):
        """Test successful password reset with valid data"""
        new_password = 'NewSecurePassword123!'
        response = self.client.post(self.url, {
            'new_password1': new_password,
            'new_password2': new_password,
        })

        # Should redirect to complete page
        self.assertRedirects(response, reverse('data_management:password_reset_complete'))

        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_password_reset_confirm_passwords_dont_match(self):
        """Test password reset with mismatched passwords"""
        response = self.client.post(self.url, {
            'new_password1': 'NewPassword123!',
            'new_password2': 'DifferentPassword123!',
        })

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        # Check that there's an error for password mismatch
        self.assertIn('new_password2', form.errors)

    def test_password_reset_confirm_empty_fields(self):
        """Test password reset with empty fields - the original bug"""
        response = self.client.post(self.url, {
            'new_password1': '',
            'new_password2': '',
        })

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        # Should have field errors for both password fields
        self.assertIn('new_password1', form.errors)

    def test_password_reset_confirm_htmx_valid_submission(self):
        """Test password reset via HTMX with valid data"""
        new_password = 'NewSecurePassword123!'
        response = self.client.post(self.url, {
            'new_password1': new_password,
            'new_password2': new_password,
        }, HTTP_HX_REQUEST='true')

        # Should return success partial
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/partials/password_reset_confirm_success.html')

        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_password_reset_confirm_htmx_invalid_submission(self):
        """Test password reset via HTMX with invalid data"""
        response = self.client.post(self.url, {
            'new_password1': '',
            'new_password2': '',
        }, HTTP_HX_REQUEST='true')

        # Should return form partial with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/partials/password_reset_confirm_form.html')
        self.assertTrue(response.context['form'].errors)

    def test_password_reset_confirm_password_too_short(self):
        """Test password reset with password that's too short"""
        response = self.client.post(self.url, {
            'new_password1': 'short',
            'new_password2': 'short',
        })

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)

    def test_password_reset_confirm_password_too_common(self):
        """Test password reset with common password"""
        response = self.client.post(self.url, {
            'new_password1': 'password123',
            'new_password2': 'password123',
        })

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        # Should have validation errors
        self.assertTrue(form.errors)

    def test_password_reset_confirm_numeric_only_password(self):
        """Test password reset with numeric-only password"""
        response = self.client.post(self.url, {
            'new_password1': '12345678',
            'new_password2': '12345678',
        })

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)

    def test_password_reset_token_used_once(self):
        """Test that password reset token can only be used once"""
        new_password = 'NewSecurePassword123!'

        # First reset should work
        response1 = self.client.post(self.url, {
            'new_password1': new_password,
            'new_password2': new_password,
        })
        self.assertRedirects(response1, reverse('data_management:password_reset_complete'))

        # Second attempt with same token should fail
        response2 = self.client.get(self.url)
        self.assertFalse(response2.context['validlink'])
