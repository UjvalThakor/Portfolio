from django.test import TestCase, Client
from django.urls import reverse
from core.models import ProfileConfig, Resume, Experience

class CoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = ProfileConfig.objects.create(
            full_name="Ujval Thakor",
            primary_title="Backend Developer",
            email="ujvalthakor14@gmail.com"
        )
        self.resume = Resume.objects.create(
            title="Ujval Thakor — Resume",
            summary="Backend developer specializing in Python & Django."
        )

    def test_home_view(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ujval")

    def test_about_view(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)

    def test_resume_view_bug001(self):
        """BUG #001: Resume template syntax rendering"""
        response = self.client.get(reverse('core:resume_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ujval Thakor")

    def test_resume_download_bug002(self):
        """BUG #002: Resume download route without crash"""
        response = self.client.get(reverse('core:resume_download'))
        self.assertIn(response.status_code, [200, 302])

    def test_sitemap_bug003(self):
        """BUG #003: Sitemap must not contain dead /work/ route and include /projects/"""
        response = self.client.get(reverse('core:sitemap_xml'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertNotIn('/work/', content)
        self.assertIn('/projects/', content)

    def test_robots_txt(self):
        response = self.client.get(reverse('core:robots_txt'))
        self.assertEqual(response.status_code, 200)

