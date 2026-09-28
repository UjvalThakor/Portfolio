import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from django.conf import settings
from core.models import ProfileConfig, Experience, Skill, Resume
from projects.models import Project, Technology
from .models import AvailabilityStatus

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"


def _load_json_file(filename: str) -> Dict[str, Any]:
    file_path = KNOWLEDGE_DIR / filename
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read knowledge file {filename}: {e}")
    return {}


class CentralKnowledgeBase:
    """
    Centralized, structured ground-truth knowledge source for Ujval's portfolio.
    Guarantees that the AI agent only speaks from verified facts,
    cross-referencing static ground-truth JSON files with live database models.
    """

    @classmethod
    def get_profile(cls) -> Dict[str, Any]:
        """Live DB ProfileConfig with fallback to profile.json"""
        json_data = _load_json_file("profile.json")
        try:
            db_profile = ProfileConfig.objects.first()
            if db_profile:
                return {
                    'name': db_profile.full_name,
                    'title': db_profile.primary_title,
                    'subtitle': db_profile.secondary_title,
                    'email': db_profile.email,
                    'location': db_profile.location,
                    'timezone': json_data.get('timezone', 'Asia/Kolkata (UTC+5:30)'),
                    'github': db_profile.github_url,
                    'linkedin': db_profile.linkedin_url,
                    'education': json_data.get('education', 'B.Tech in Computer Engineering (2022 - 2026)'),
                    'status': db_profile.current_status,
                    'about': db_profile.about_editorial_text,
                    'short_bio': db_profile.short_positioning,
                }
        except Exception as e:
            logger.warning(f"DB profile fetch error: {e}")
        return json_data

    @classmethod
    def get_availability(cls) -> Dict[str, Any]:
        """
        Live admin-controlled availability status.
        Reads live database model AvailabilityStatus so changes made
        in the admin interface reflect immediately without code edits.
        """
        try:
            avail = AvailabilityStatus.get_current()
            return {
                'status': avail.status,
                'status_display': avail.get_status_display(),
                'headline': avail.headline,
                'project_work': avail.project_work,
                'freelance': avail.freelance,
                'full_time': avail.full_time,
                'internship': avail.internship,
                'notes': avail.notes,
                'last_updated': avail.last_updated.isoformat(),
                'is_available': avail.status in ('AVAILABLE', 'LIMITED'),
            }
        except Exception as e:
            logger.warning(f"DB availability fetch error: {e}")
            json_data = _load_json_file("availability.json")
            return {
                'status': json_data.get('status', 'AVAILABLE'),
                'status_display': 'Available for Projects & Roles',
                'headline': json_data.get('headline', 'Available for selected projects'),
                'project_work': json_data.get('project_work', True),
                'freelance': json_data.get('freelance', True),
                'full_time': json_data.get('full_time', True),
                'internship': json_data.get('internship', False),
                'notes': json_data.get('notes', ''),
                'last_updated': json_data.get('last_updated', ''),
                'is_available': True,
            }

    @classmethod
    def get_skills(cls, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Verified technical skills from DB and skills.json"""
        json_data = _load_json_file("skills.json")
        try:
            skills_qs = Skill.objects.all().order_by('category', 'order', 'name')
            if skills_qs.exists():
                results = []
                for s in skills_qs:
                    cat_code = s.category.lower()
                    if category and category.lower() not in cat_code and category.lower() not in s.get_category_display().lower():
                        continue
                    results.append({
                        'name': s.name,
                        'category': s.get_category_display(),
                        'badge': s.badge_label or 'Verified',
                    })
                return results
        except Exception as e:
            logger.warning(f"DB skills fetch error: {e}")

        # Fallback to skills.json
        flat_skills = []
        for cat in json_data.get('categories', []):
            cat_name = cat.get('name', '')
            if category and category.lower() not in cat_name.lower():
                continue
            for item in cat.get('skills', []):
                flat_skills.append({
                    'name': item.get('name'),
                    'category': cat_name,
                    'badge': item.get('badge', ''),
                })
        return flat_skills

    @classmethod
    def get_projects(cls) -> List[Dict[str, Any]]:
        """Verified projects from DB with fallback to projects.json"""
        try:
            db_projects = Project.objects.all().prefetch_related('technologies').order_by('order', 'id')
            if db_projects.exists():
                projects_list = []
                for p in db_projects:
                    techs = [t.name for t in p.technologies.all()]
                    projects_list.append({
                        'id': p.slug,
                        'name': p.title,
                        'number': p.project_number,
                        'category': p.category,
                        'year': p.year,
                        'short_description': p.short_description,
                        'description': p.description,
                        'problem_solved': p.solution,
                        'challenge': p.challenge,
                        'solution': p.solution,
                        'technologies': techs,
                        'features': p.get_features_list(),
                        'status': 'active',
                        'github_available': bool(p.github_url),
                        'github_url': p.github_url or 'https://github.com/ujvalthakor',
                        'portfolio_url': f"/projects/{p.slug}/",
                    })
                return projects_list
        except Exception as e:
            logger.warning(f"DB projects fetch error: {e}")

        return _load_json_file("projects.json").get('projects', [])

    @classmethod
    def get_services(cls) -> List[Dict[str, Any]]:
        """Verified service offerings from services.json"""
        return _load_json_file("services.json").get('services', [])

    @classmethod
    def get_experience(cls) -> Dict[str, Any]:
        """Verified experience & education"""
        json_data = _load_json_file("experience.json")
        try:
            exps = Experience.objects.all().order_by('order', '-id')
            if exps.exists():
                db_experiences = []
                for e in exps:
                    db_experiences.append({
                        'role': e.role,
                        'organization': e.company,
                        'location': e.location,
                        'period': f"{e.start_date} – {e.end_date}",
                        'type': e.get_experience_type_display(),
                        'highlights': e.get_highlights_list(),
                    })
                json_data['experiences'] = db_experiences
        except Exception as e:
            logger.warning(f"DB experience fetch error: {e}")
        return json_data

    @classmethod
    def get_faq(cls) -> List[Dict[str, str]]:
        """FAQ database"""
        return _load_json_file("faq.json").get('faqs', [])

    @classmethod
    def get_contact_info(cls) -> Dict[str, Any]:
        """Contact info"""
        return _load_json_file("contact.json")

    @classmethod
    def build_system_context(cls) -> str:
        """
        Assembles a comprehensive, structured text context
        for prompt injection into external LLMs.
        """
        prof = cls.get_profile()
        avail = cls.get_availability()
        projs = cls.get_projects()
        skills = cls.get_skills()
        services = cls.get_services()
        exps = cls.get_experience()

        lines = [
            "### UJVAL THAKOR — PORTFOLIO SOURCE OF TRUTH ###",
            f"Developer: {prof.get('name')} | Title: {prof.get('title')} ({prof.get('subtitle')})",
            f"Location: {prof.get('location')} | Timezone: {prof.get('timezone')}",
            f"Email: {prof.get('email')} | GitHub: {prof.get('github')} | LinkedIn: {prof.get('linkedin')}",
            f"Education: {prof.get('education')}",
            f"\n### LIVE AVAILABILITY STATUS ###",
            f"Current Bandwidth: {avail.get('status')} ({avail.get('status_display')})",
            f"Headline: {avail.get('headline')}",
            f"Project/Freelance Work Open: {'YES' if avail.get('project_work') else 'NO'}",
            f"Full-Time Open: {'YES' if avail.get('full_time') else 'NO'}",
            f"Notes: {avail.get('notes')}",
            f"\n### VERIFIED SKILLS ###",
        ]

        for s in skills:
            lines.append(f"- {s.get('name')} [{s.get('category')}] ({s.get('badge')})")

        lines.append("\n### VERIFIED PROJECTS ###")
        for p in projs:
            lines.append(f"\nProject: {p.get('name')} ({p.get('category')}, {p.get('year')})")
            lines.append(f"  Summary: {p.get('short_description')}")
            lines.append(f"  Tech: {', '.join(p.get('technologies', []))}")
            lines.append(f"  Problem Solved: {p.get('problem_solved')}")
            lines.append(f"  URL: {p.get('portfolio_url')}")

        lines.append("\n### SERVICES OFFERED ###")
        for s in services:
            lines.append(f"- {s.get('title')}: {s.get('summary')}")
            lines.append(f"  Best for: {s.get('best_for')}")

        lines.append("\n### IMPORTANT GROUND RULES ###")
        lines.append("1. Never hallucinate skills or projects not listed above.")
        lines.append("2. When asked about availability, check the live availability status.")
        lines.append("3. Do not quote fixed prices. Offer to collect requirements for a custom estimate.")
        lines.append("4. For client or recruiter intent, engage in conversational qualification.")

        return "\n".join(lines)
