import json
from django.test import TestCase, Client
from django.urls import reverse

from core.models import ProfileConfig, Experience, Skill, Resume
from projects.models import Project, Technology
from chatbot.services import PortfolioKnowledgeBase, GroundedPortfolioEngine, ChatbotService

class ChatbotIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Seed test portfolio data
        self.profile = ProfileConfig.objects.create(
            full_name="Ujval Thakor",
            primary_title="Backend Developer",
            secondary_title="Python • Django • REST APIs • AI/ML",
            email="ujvalthakor14@gmail.com",
            location="Surat, Gujarat, India",
            available_for_work=True,
            about_editorial_text="Backend developer specializing in resilient Django systems.",
        )

        self.tech_python = Technology.objects.create(name="Python", category="BACKEND")
        self.tech_django = Technology.objects.create(name="Django", category="BACKEND")
        self.tech_opencv = Technology.objects.create(name="OpenCV", category="AI_CV")

        self.skill_python = Skill.objects.create(name="Python 3.x", category="BACKEND")
        self.skill_django = Skill.objects.create(name="Django", category="BACKEND")

        self.project_beauty = Project.objects.create(
            title="BeautyCare AI",
            slug="beautycare-ai",
            project_number="01",
            category="AI & REST APIs",
            year="2026",
            short_description="Django-based AI-powered application orchestrating skin analysis via REST APIs.",
            description="BeautyCare AI is an intelligent backend system engineered to deliver tailored skincare diagnostics.",
            challenge="External AI inference endpoints introduced latency spikes.",
            solution="Structured a non-blocking service abstraction that caches diagnostic signatures in Redis.",
            featured=True,
        )
        self.project_beauty.technologies.add(self.tech_python, self.tech_django)

        self.project_fabric = Project.objects.create(
            title="Fabric Fault Detection",
            slug="fabric-fault-detection",
            project_number="02",
            category="Real-Time Computer Vision",
            year="2025",
            short_description="Real-time computer vision quality inspection system for textile manufacturing.",
            description="Industrial quality control vision system automating defect detection on textile conveyor lines.",
            challenge="High-resolution video streaming choked standard single-threaded Python execution.",
            solution="Decoupled frame capture from image processing using Python threading and thread-safe queues.",
            featured=True,
        )
        self.project_fabric.technologies.add(self.tech_python, self.tech_opencv)

        self.experience = Experience.objects.create(
            company="B.Tech in Computer Engineering",
            role="Engineering Student",
            location="Gujarat, India",
            start_date="2022",
            end_date="2026",
            is_current=True,
            description="Rigorous computer science curriculum emphasizing Data Structures, Algorithms, and DBMS.",
        )

        self.resume = Resume.objects.create(
            title="Ujval Thakor Resume",
            summary="B.Tech Computer Engineering student with hands-on Python and Django development experience.",
            is_active=True,
        )

    def test_knowledge_base_extraction(self):
        """Verify dynamic database aggregation without hardcoded answers"""
        prof = PortfolioKnowledgeBase.get_profile()
        self.assertEqual(prof['name'], "Ujval Thakor")
        self.assertEqual(prof['email'], "ujvalthakor14@gmail.com")

        projs = PortfolioKnowledgeBase.get_projects()
        self.assertEqual(len(projs), 2)
        self.assertEqual(projs[0]['title'], "BeautyCare AI")

        skills = PortfolioKnowledgeBase.get_skills()
        self.assertGreaterEqual(len(skills), 2)

        summary = PortfolioKnowledgeBase.get_full_context_summary()
        self.assertIn("BeautyCare AI", summary)
        self.assertIn("Ujval Thakor", summary)

    def test_chat_message_greeting(self):
        """Chatbot responds naturally to standard greetings"""
        res = self.client.post(
            reverse('chatbot:message'),
            json.dumps({'message': 'Hello!'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn("Ujval Thakor's Portfolio Assistant", data['reply'])

    def test_chat_message_contact_inquiry(self):
        """Chatbot provides accurate contact information and link to /contact/"""
        res = self.client.post(
            reverse('chatbot:message'),
            json.dumps({'message': 'How can I contact Ujval?'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("ujvalthakor14@gmail.com", data['reply'])
        self.assertIn("/contact/", data['reply'])

    def test_chat_message_skills_inquiry(self):
        """Chatbot explains Ujval's tech stack accurately"""
        res = self.client.post(
            reverse('chatbot:message'),
            json.dumps({'message': 'What technologies and skills does Ujval use?'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("Python", data['reply'])
        self.assertIn("Django", data['reply'])

    def test_chat_message_specific_project(self):
        """Chatbot details a specific project with challenge and solution"""
        res = self.client.post(
            reverse('chatbot:message'),
            json.dumps({'message': 'Tell me about BeautyCare AI'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("BeautyCare AI", data['reply'])
        self.assertIn("/projects/beautycare-ai/", data['reply'])
        self.assertIn("latency spikes", data['reply'])

    def test_chat_follow_up_context(self):
        """Chatbot understands anaphoric follow-up questions referencing previous turn"""
        # First turn: ask about Fabric Fault Detection
        self.client.post(
            reverse('chatbot:message'),
            json.dumps({'message': 'Tell me about Fabric Fault Detection'}),
            content_type='application/json'
        )
        # Second turn: ask "what was the challenge in that?"
        res2 = self.client.post(
            reverse('chatbot:message'),
            json.dumps({'message': 'What was the challenge in that?'}),
            content_type='application/json'
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertIn("Fabric Fault Detection", data2['reply'])
        self.assertIn("video streaming", data2['reply'].lower())

    def test_chat_unknown_question_honest_fallback(self):
        """Chatbot refuses to hallucinate unknown facts and guides to Contact"""
        res = self.client.post(
            reverse('chatbot:message'),
            json.dumps({'message': 'What is the refund policy for airline flight tickets?'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("I don't have enough verified information", data['reply'])
        self.assertIn("/contact/", data['reply'])

    def test_chat_pricing_honest_answer(self):
        """Chatbot accurately clarifies that fixed public rates are not published and guides to Contact"""
        res = self.client.post(
            reverse('chatbot:message'),
            json.dumps({'message': 'What are your prices and rates?'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("does not publish fixed public pricing", data['reply'])
        self.assertIn("/contact/", data['reply'])

    def test_chat_validation_empty_message(self):
        """Chatbot handles empty inputs gracefully without throwing 500"""
        res = self.client.post(
            reverse('chatbot:message'),
            json.dumps({'message': '   '}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn("Please provide a question", data['reply'])

    def test_chat_validation_too_long_message(self):
        """Chatbot rejects excessively long payloads to prevent abuse"""
        res = self.client.post(
            reverse('chatbot:message'),
            json.dumps({'message': 'A' * 600}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn("too long", data['reply'])

    def test_chat_clear_session(self):
        """Reset conversation endpoint clears session history"""
        self.client.post(
            reverse('chatbot:message'),
            json.dumps({'message': 'Hello'}),
            content_type='application/json'
        )
        res_clear = self.client.post(reverse('chatbot:clear'))
        self.assertEqual(res_clear.status_code, 200)
        self.assertEqual(res_clear.json()['status'], 'cleared')

    def test_chat_suggestions_endpoint(self):
        """Suggestions endpoint returns contextual prompt chips"""
        res = self.client.get(reverse('chatbot:suggestions'))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn('suggestions', data)
        self.assertGreater(len(data['suggestions']), 0)
