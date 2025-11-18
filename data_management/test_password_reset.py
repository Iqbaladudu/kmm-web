"""
Test for password reset functionality
"""
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse


class PasswordResetViewTest(TestCase):
    """Test password reset request view"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.url = reverse('data_management:password_reset')

    def test_password_reset_page_loads(self):
        """Test that password reset page loads successfully"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')

    def test_password_reset_form_submission_valid_email(self):
        """Test password reset with valid email sends email"""
        response = self.client.post(self.url, {
            'email': 'test@example.com'
        })

        # Should redirect to done page for non-HTMX request
        self.assertRedirects(response, reverse('data_management:password_reset_done'))

        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('test@example.com', mail.outbox[0].to)

    def test_password_reset_form_submission_invalid_email(self):
        """Test password reset with non-existent email still shows success (security)"""
        response = self.client.post(self.url, {
            'email': 'nonexistent@example.com'
        })

        # Should still redirect to done page (security measure)
        self.assertRedirects(response, reverse('data_management:password_reset_done'))

        # No email should be sent for non-existent email
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_htmx_request(self):
        """Test password reset with HTMX request"""
        response = self.client.post(
            self.url,
            {'email': 'test@example.com'},
            HTTP_HX_REQUEST='true'
        )

        # Should return 200 and the partial template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/partials/password_reset_form_partial.html')

        # Should contain success message
        self.assertContains(response, 'Link reset password telah dikirim ke email Anda')

        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_htmx_request_empty_email(self):
        """Test password reset with HTMX request and empty email"""
        response = self.client.post(
            self.url,
            {'email': ''},
            HTTP_HX_REQUEST='true'
        )

        # Should return 200 with form errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/partials/password_reset_form_partial.html')

        # Should not send any email
        self.assertEqual(len(mail.outbox), 0)
