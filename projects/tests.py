from django.test import TestCase, Client
from django.urls import reverse
from projects.models import Project, Technology

class ProjectsViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.python_tech = Technology.objects.create(name="Python", category="BACKEND")
        self.project = Project.objects.create(
            title="Distributed Task Engine",
            slug="distributed-task-engine",
            project_number="01",
            category="BACKEND",
            short_description="High-throughput asynchronous task engine.",
            description="Detailed architecture breakdown of the distributed task engine.",
            challenge="Processing burst loads without blocking HTTP workers.",
            solution="Decoupled queue architecture with Celery and Redis.",
            featured=True,
        )
        self.project.technologies.add(self.python_tech)

    def test_project_list_view(self):
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Distributed Task Engine")

    def test_project_list_category_filter(self):
        response = self.client.get(reverse('projects:list') + '?category=BACKEND')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Distributed Task Engine")

    def test_project_detail_view(self):
        response = self.client.get(reverse('projects:detail', kwargs={'slug': self.project.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Distributed Task Engine")

