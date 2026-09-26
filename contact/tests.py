from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core import mail
from contact.models import ContactMessage

class ContactViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_contact_page_get(self):
        response = self.client.get(reverse('contact:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'contact-form-wrapper')

    def test_contact_honeypot_bug006(self):
        """BUG #006: Honeypot submission renders non-field errors"""
        payload = {
            'name': 'Bot Submitter',
            'email': 'bot@example.com',
            'subject': 'Spam subject',
            'message': 'This is spam text with minimum length satisfied',
            'website_check': 'bot_detected',
        }
        response = self.client.post(reverse('contact:contact_submit'), payload, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Spam detected. Bot rejection trigger.')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_contact_email_dispatch_bug007(self):
        """BUG #007: Valid contact submission sends email notification"""
        mail.outbox = []
        payload = {
            'name': 'Sarah Connor',
            'email': 'sarah@resistance.org',
            'subject': 'Architecture inquiry for systems',
            'message': 'Hello Ujval, we have a backend engineering opportunity.',
            'website_check': '',
        }
        response = self.client.post(reverse('contact:contact_submit'), payload, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('[Portfolio Contact]', mail.outbox[0].subject)
        self.assertIn('sarah@resistance.org', mail.outbox[0].body)

