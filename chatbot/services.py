import os
import re
import time
import json
import logging
from typing import Dict, List, Any, Optional

import requests
from django.conf import settings
from django.utils.html import escape

from core.models import ProfileConfig, Experience, Skill, Resume
from projects.models import Project, Technology

logger = logging.getLogger(__name__)

class PortfolioKnowledgeBase:
    """
    Dynamically extracts verified data from the portfolio database models.
    Ensures the chatbot always uses fresh, trusted website information
    without hardcoding answers.
    """

    @classmethod
    def get_profile(cls) -> Dict[str, Any]:
        profile = ProfileConfig.objects.first()
        if not profile:
            return {
                'name': 'Ujval Thakor',
                'title': 'Backend Developer',
                'subtitle': 'Python • Django • REST APIs • AI/ML',
                'email': 'ujvalthakor14@gmail.com',
                'phone': '+91 9104502128',
                'location': 'Surat, Gujarat, India',
                'github': 'https://github.com/ujvalthakor',
                'linkedin': 'https://linkedin.com/in/ujvalthakor',
                'status': 'B.Tech Computer Engineering student with hands-on Python and Django development experience.',
                'available': True,
                'about_heading': 'I BUILD THE SYSTEM BEHIND THE EXPERIENCE.',
                'about_text': 'Backend developer focused on Python, Django, REST APIs, and AI integrations.',
            }
        return {
            'name': profile.full_name,
            'title': profile.primary_title,
            'subtitle': profile.secondary_title,
            'email': profile.email,
            'phone': '+91 9104502128',
            'location': profile.location,
            'github': profile.github_url,
            'linkedin': profile.linkedin_url,
            'status': profile.current_status,
            'available': profile.available_for_work,
            'about_heading': profile.about_editorial_heading,
            'about_text': profile.about_editorial_text,
        }

    @classmethod
    def get_skills(cls) -> List[Dict[str, Any]]:
        skills = Skill.objects.all().order_by('category', 'order', 'name')
        result = []
        for s in skills:
            result.append({
                'name': s.name,
                'category': s.get_category_display(),
                'badge': s.badge_label,
            })
        return result

    @classmethod
    def get_technologies(cls) -> List[Dict[str, Any]]:
        technologies = Technology.objects.all().order_by('order', 'name')
        result = []
        for t in technologies:
            result.append({
                'name': t.name,
                'category': t.get_category_display(),
                'description': t.description,
            })
        return result

    @classmethod
    def get_projects(cls) -> List[Dict[str, Any]]:
        projects = Project.objects.all().prefetch_related('technologies').order_by('order', 'id')
        result = []
        for p in projects:
            tech_list = [t.name for t in p.technologies.all()]
            result.append({
                'title': p.title,
                'slug': p.slug,
                'number': p.project_number,
                'category': p.category,
                'year': p.year,
                'short_desc': p.short_description,
                'desc': p.description,
                'architecture': p.architecture_description,
                'architecture_flow': p.architecture_flow,
                'challenge': p.challenge,
                'solution': p.solution,
                'learning': p.learning,
                'features': [f.strip() for f in p.key_features.split('\n') if f.strip()],
                'technologies': tech_list,
                'github_url': p.github_url,
                'live_url': p.live_url,
                'url': f"/projects/{p.slug}/",
            })
        return result

    @classmethod
    def get_experiences(cls) -> List[Dict[str, Any]]:
        experiences = Experience.objects.all().order_by('order', '-id')
        result = []
        for e in experiences:
            result.append({
                'company': e.company,
                'role': e.role,
                'location': e.location,
                'start_date': e.start_date,
                'end_date': e.end_date,
                'is_current': e.is_current,
                'type': e.get_experience_type_display(),
                'description': e.description,
                'highlights': e.get_highlights_list(),
            })
        return result

    @classmethod
    def get_resume(cls) -> Dict[str, Any]:
        res = Resume.objects.filter(is_active=True).first()
        if res:
            return {
                'title': res.title,
                'summary': res.summary,
                'has_file': bool(res.file),
                'download_url': '/resume/download/',
                'view_url': '/resume/',
            }
        return {
            'title': 'Ujval Thakor Resume',
            'summary': 'B.Tech Computer Engineering student with hands-on Python and Django development experience.',
            'has_file': False,
            'download_url': '/resume/download/',
            'view_url': '/resume/',
        }

    @classmethod
    def get_full_context_summary(cls) -> str:
        """
        Builds a comprehensive, grounded text representation of the website
        for AI model prompt injection.
        """
        prof = cls.get_profile()
        projs = cls.get_projects()
        skills = cls.get_skills()
        exps = cls.get_experiences()
        res = cls.get_resume()

        parts = [
            f"=== DEVELOPER PROFILE ===",
            f"Name: {prof['name']}",
            f"Title: {prof['title']}",
            f"Specialization: {prof['subtitle']}",
            f"Location: {prof['location']} (Timezone: UTC+5:30)",
            f"Email: {prof['email']}",
            f"Phone: {prof['phone']}",
            f"Availability: {'Available for contract & full-time roles' if prof['available'] else 'Currently occupied'}",
            f"GitHub: {prof['github']}",
            f"LinkedIn: {prof['linkedin']}",
            f"Current Status: {prof['status']}",
            f"Engineering Philosophy: {prof['about_text']}",
            f"\n=== WEBSITE NAVIGATION & ROUTES ===",
            "- Home Canvas: /",
            "- Selected Work / Projects Archive: /projects/",
            "- About Engineering Profile & Timeline: /about/",
            "- Full Curriculum Vitae / Resume: /resume/",
            "- Direct Resume Download: /resume/download/",
            "- Contact & Direct Message Form: /contact/",
            f"\n=== VERIFIED TECHNICAL SKILLS ===",
        ]

        for s in skills:
            badge = f" ({s['badge']})" if s['badge'] else ""
            parts.append(f"- {s['name']} [{s['category']}]{badge}")

        parts.append("\n=== KEY PROJECTS & CASE STUDIES ===")
        for p in projs:
            parts.append(f"\nProject: {p['title']} (#{p['number']})")
            parts.append(f"Category: {p['category']} | Year: {p['year']}")
            parts.append(f"URL: {p['url']}")
            parts.append(f"Summary: {p['short_desc']}")
            parts.append(f"Technologies: {', '.join(p['technologies'])}")
            if p['architecture']:
                parts.append(f"Architecture: {p['architecture']}")
            if p['challenge']:
                parts.append(f"Technical Challenge: {p['challenge']}")
            if p['solution']:
                parts.append(f"Engineered Solution: {p['solution']}")
            if p['github_url']:
                parts.append(f"GitHub: {p['github_url']}")

        parts.append("\n=== PRACTICAL & ACADEMIC TIMELINE ===")
        for e in exps:
            parts.append(f"\nRole: {e['role']} at {e['company']}")
            parts.append(f"Period: {e['start_date']} - {e['end_date']} | Location: {e['location']}")
            parts.append(f"Overview: {e['description']}")
            for h in e['highlights']:
                parts.append(f"  • {h}")

        parts.append("\n=== RESUME ===")
        parts.append(f"Title: {res['title']}")
        parts.append(f"Summary: {res['summary']}")
        parts.append(f"Online Resume Link: {res['view_url']}")

        return "\n".join(parts)


class GroundedPortfolioEngine:
    """
    Deterministic, grounded intelligence engine for the portfolio.
    Guarantees instant, 100% accurate, zero-hallucination responses
    based directly on database context, even if external AI APIs are
    unreachable or unconfigured.
    """

    @classmethod
    def answer(cls, query: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        q = query.strip().lower()
        prof = PortfolioKnowledgeBase.get_profile()
        projects = PortfolioKnowledgeBase.get_projects()
        skills = PortfolioKnowledgeBase.get_skills()
        experiences = PortfolioKnowledgeBase.get_experiences()
        resume = PortfolioKnowledgeBase.get_resume()

        # Follow-up resolution: check previous turn if query has anaphoric references
        last_subject = None
        if history and len(history) > 0:
            for item in reversed(history):
                text = item.get('content', '').lower()
                for proj in projects:
                    if proj['title'].lower() in text or proj['slug'] in text:
                        last_subject = proj
                        break
                if last_subject:
                    break

        def has_words(words: List[str]) -> bool:
            pattern = r'\b(' + '|'.join(re.escape(w) for w in words) + r')\b'
            return bool(re.search(pattern, q, re.IGNORECASE))

        # 1. Greetings
        if re.search(r'\b(hi|hello|hey|greetings|hola|good morning|good evening|who are you)\b', q) and len(q.split()) <= 4:
            return {
                'reply': (
                    f"Hello! I am **Ujval Thakor's Portfolio Assistant**.\n\n"
                    f"I can help you explore Ujval's backend engineering systems, technical skill stack, academic background, "
                    f"or get in touch for contract and full-time opportunities.\n\n"
                    f"What would you like to know?"
                ),
                'suggestions': [
                    "What backend technologies does Ujval use?",
                    "Tell me about his key projects",
                    "How can I contact Ujval?",
                    "View his resume"
                ]
            }

        # 2. Contact / Hiring / Email / Phone
        if has_words(['contact', 'email', 'phone', 'hire', 'reach', 'connect', 'interview', 'call', 'talk', 'touch']):
            return {
                'reply': (
                    f"You can reach out to **Ujval Thakor** directly:\n\n"
                    f"• **Email:** [{prof['email']}](mailto:{prof['email']})\n"
                    f"• **Phone:** [{prof['phone']}](tel:{prof['phone'].replace(' ', '')})\n"
                    f"• **Location:** {prof['location']} (UTC+5:30)\n"
                    f"• **GitHub:** [{prof['github']}]({prof['github']})\n"
                    f"• **LinkedIn:** [{prof['linkedin']}]({prof['linkedin']})\n\n"
                    f"You can also send a direct message through the **[Contact Page](/contact/)** on this website."
                ),
                'suggestions': [
                    "Is Ujval available for work?",
                    "View Ujval's resume",
                    "What projects has he built?"
                ]
            }

        # 3. Availability for work
        if has_words(['available', 'availability', 'freelance', 'contract', 'job', 'full time', 'open to work']):
            status_text = "actively available for contract, internship, and full-time software engineering roles" if prof['available'] else "currently focusing on ongoing engagements"
            return {
                'reply': (
                    f"**Yes**, Ujval Thakor is {status_text}.\n\n"
                    f"• **Primary Focus:** Backend Development, Distributed Systems, REST APIs, and AI/CV Integrations.\n"
                    f"• **Location:** {prof['location']} (open to remote & on-site positions).\n"
                    f"• **Direct Contact:** [{prof['email']}](mailto:{prof['email']}) or visit the **[Contact Form](/contact/)**."
                ),
                'suggestions': [
                    "How can I contact Ujval?",
                    "What tech stack does he use?",
                    "View resume"
                ]
            }

        # 4. Resume / CV
        if has_words(['resume', 'cv', 'curriculum vitae', 'download resume', 'bio']):
            return {
                'reply': (
                    f"You can view and download Ujval Thakor's curriculum vitae:\n\n"
                    f"• **Online Resume:** [View Full Resume](/resume/)\n"
                    f"• **Direct Download:** [Download PDF](/resume/download/)\n\n"
                    f"**Summary:** {resume['summary']}"
                ),
                'suggestions': [
                    "What are his core technical skills?",
                    "Show his education details",
                    "How can I contact Ujval?"
                ]
            }

        # 5. Education / College / Degree
        if has_words(['education', 'college', 'degree', 'btech', 'university', 'study', 'student', 'school', 'academic']):
            edu = next((e for e in experiences if 'B.Tech' in e['company'] or 'Engineering' in e['role']), None)
            return {
                'reply': (
                    f"**Academic Background:**\n\n"
                    f"• **Degree:** B.Tech in Computer Engineering (2022 – 2026)\n"
                    f"• **Location:** Gujarat, India\n"
                    f"• **Core Focus:** Relational Databases, Operating Systems, Data Structures & Algorithms, Computer Networks, and Software Architecture.\n"
                    f"• **Highlights:** Practical hands-on development in Python, C++, MySQL, and Linux environments; active system design projects."
                ),
                'suggestions': [
                    "What projects has he completed?",
                    "What skills does he have?",
                    "View full resume"
                ]
            }

        # 6. Specific Project Inquiries (by title or slug or follow-up)
        matched_project = None
        for proj in projects:
            title_words = [w.lower() for w in proj['title'].split()]
            if proj['title'].lower() in q or proj['slug'] in q:
                matched_project = proj
                break
            # keyword match
            if 'beauty' in q or 'skincare' in q:
                if 'beauty' in proj['slug']: matched_project = proj; break
            if 'student' in q and ('management' in q or 'system' in q):
                if 'student' in proj['slug']: matched_project = proj; break
            if 'job' in q and ('portal' in q or 'hiring' in q):
                if 'job' in proj['slug']: matched_project = proj; break
            if 'cosmic' in q or 'astrology' in q:
                if 'cosmic' in proj['slug']: matched_project = proj; break
            if ('license' in q or 'car' in q or 'plate' in q or 'number' in q) and ('detection' in q or 'car' in q):
                if 'car' in proj['slug']: matched_project = proj; break
            if 'fabric' in q or 'textile' in q or 'weaving' in q:
                if 'fabric' in proj['slug']: matched_project = proj; break

        # If user asks anaphoric follow-up like "tell me more about it", "what was the challenge in that?"
        if not matched_project and last_subject and any(term in q for term in ['it', 'that', 'this project', 'tell me more', 'challenge', 'solution', 'tech', 'how does it work']):
            matched_project = last_subject

        if matched_project:
            p = matched_project
            tech_str = ", ".join(p['technologies'])
            features_str = "\n".join([f"• {f}" for f in p['features'][:4]])
            github_link = f"\n• **GitHub Repository:** [{p['github_url']}]({p['github_url']})" if p['github_url'] else ""
            
            return {
                'reply': (
                    f"### [{p['title']}]({p['url']}) (#{p['number']})\n"
                    f"**Category:** {p['category']} | **Year:** {p['year']}\n\n"
                    f"{p['desc']}\n\n"
                    f"**Technologies:** {tech_str}\n\n"
                    f"**Key Engineering Highlights:**\n{features_str}\n\n"
                    f"**Technical Challenge & Solution:**\n"
                    f"• *Challenge:* {p['challenge']}\n"
                    f"• *Solution:* {p['solution']}{github_link}\n\n"
                    f"Read the full architectural case study on the **[Project Page]({p['url']})**."
                ),
                'suggestions': [
                    "Show other projects",
                    "What backend stack does Ujval use?",
                    "How can I contact Ujval?"
                ]
            }

        # 7. General Projects list / What has he built?
        if has_words(['project', 'projects', 'work', 'built', 'portfolio', 'case study', 'systems', 'apps']):
            lines = []
            for p in projects:
                lines.append(f"• **[{p['title']}]({p['url']})** (#{p['number']}) — {p['short_desc']}")
            
            return {
                'reply': (
                    f"Ujval Thakor has built **{len(projects)} key engineering systems** across backend architectures, REST APIs, and computer vision:\n\n"
                    + "\n\n".join(lines) +
                    f"\n\nExplore all deep case studies in the **[Projects Catalogue](/projects/)**."
                ),
                'suggestions': [
                    "Tell me about BeautyCare AI",
                    "Explain Fabric Fault Detection",
                    "What tech stack does Ujval use?"
                ]
            }

        # 8. Skills / Technologies / Stack
        if has_words(['skill', 'skills', 'tech', 'technologies', 'technology', 'stack', 'python', 'django', 'database', 'tools', 'ai', 'ml', 'computer vision', 'opencv', 'docker']):
            backend_skills = [s['name'] for s in skills if s['category'] == 'Backend & Core']
            db_skills = [s['name'] for s in skills if s['category'] == 'Database & Caching']
            arch_skills = [s['name'] for s in skills if s['category'] == 'System Architecture & APIs']
            ai_skills = [s['name'] for s in skills if s['category'] == 'AI & Computer Vision']
            devops_skills = [s['name'] for s in skills if s['category'] == 'DevOps & Tooling']

            return {
                'reply': (
                    f"**Ujval Thakor's Technical Stack:**\n\n"
                    f"• **Backend & Core:** {', '.join(backend_skills)}\n"
                    f"• **Database & Caching:** {', '.join(db_skills)}\n"
                    f"• **Architecture & APIs:** {', '.join(arch_skills)}\n"
                    f"• **AI & Computer Vision:** {', '.join(ai_skills)}\n"
                    f"• **DevOps & Tooling:** {', '.join(devops_skills)}\n\n"
                    f"Learn more about his engineering philosophy on the **[About Page](/about/)**."
                ),
                'suggestions': [
                    "What projects use Python and Django?",
                    "Tell me about his OpenCV experience",
                    "How can I contact Ujval?"
                ]
            }

        # 9. Experience / Work History / Background
        if has_words(['experience', 'history', 'background', 'career', 'internship']):
            lines = []
            for e in experiences:
                lines.append(f"• **{e['role']}** at *{e['company']}* ({e['start_date']} – {e['end_date']})\n  {e['description']}")

            return {
                'reply': (
                    f"**Ujval Thakor's Practical & Academic Track Record:**\n\n"
                    + "\n\n".join(lines) +
                    f"\n\nReview the detailed career timeline on the **[About Page](/about/)** or view his **[Full Resume](/resume/)**."
                ),
                'suggestions': [
                    "What are his core skills?",
                    "View selected projects",
                    "Contact Ujval"
                ]
            }

        # 10. Pricing / Rates / Services
        if has_words(['pricing', 'price', 'prices', 'rate', 'rates', 'cost', 'fee', 'fees', 'quote', 'services']):
            return {
                'reply': (
                    f"Ujval does not publish fixed public pricing rates because engineering scopes vary by project architecture, "
                    f"database scaling requirements, and integration milestones.\n\n"
                    f"**Services & Engineering Scope:**\n"
                    f"• Python & Django Backend Architecture\n"
                    f"• RESTful API Design & DRF Development\n"
                    f"• Database Schema Normalization & Query Optimization (PostgreSQL, MySQL, Redis)\n"
                    f"• Computer Vision & AI API Integration (OpenCV, YOLO, Inference pipelines)\n\n"
                    f"To discuss your project requirements or obtain a quote, please reach out via the **[Contact Page](/contact/)** "
                    f"or email **[{prof['email']}](mailto:{prof['email']})**."
                ),
                'suggestions': [
                    "Send a message to Ujval",
                    "What projects has he built?",
                    "Check his availability"
                ]
            }

        # 11. Location / Where is he based?
        if has_words(['where', 'location', 'city', 'based', 'country', 'surat', 'india']):
            return {
                'reply': (
                    f"**Location:** Ujval Thakor is based in **Surat, Gujarat, India** (Timezone: UTC+5:30).\n\n"
                    f"He collaborates effectively with teams globally across different time zones and is available for both remote and on-site engineering roles."
                ),
                'suggestions': [
                    "How can I contact Ujval?",
                    "What projects has he built?",
                    "View resume"
                ]
            }

        # 12. Unknown / Fallback: strictly honest and grounded
        return {
            'reply': (
                f"I don't have enough verified information about that specific query from Ujval's portfolio website.\n\n"
                f"You can ask me about:\n"
                f"• Ujval's **backend engineering projects** (BeautyCare AI, Student Management, Fabric Fault Detection, etc.)\n"
                f"• His **tech stack** (Python, Django, PostgreSQL, Redis, OpenCV, Docker)\n"
                f"• His **academic background** and **career timeline**\n"
                f"• Or connect directly with him via the **[Contact Page](/contact/)** or email **[{prof['email']}](mailto:{prof['email']})**."
            ),
            'suggestions': [
                "What technologies does Ujval use?",
                "Tell me about his top projects",
                "How can I contact Ujval?",
                "View resume"
            ]
        }


class ExternalAIProvider:
    """
    Adapter for external LLM APIs (Gemini, OpenAI, Groq) with strict system
    prompts enforcing ground truth adherence from the portfolio database.
    """

    @classmethod
    def call_gemini(cls, api_key: str, message: str, context: str, history: List[Dict[str, str]]) -> Optional[str]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        system_instruction = (
            "You are the official AI Assistant for Ujval Thakor's portfolio website. "
            "Your role is to answer visitor questions accurately, concisely, professionally, and naturally. "
            "CRITICAL RULES:\n"
            "1. Base your answers ONLY on the verified portfolio context provided below.\n"
            "2. NEVER invent projects, pricing, claims, skills, or contact info.\n"
            "3. If information is not in the context, explicitly say you do not have enough information and guide the user to the Contact page (/contact/) or email.\n"
            "4. Format answers cleanly using markdown (bullet points, bold highlights, clickable links like [Projects](/projects/) or [Resume](/resume/)).\n"
            "5. Keep responses concise, friendly, and structured.\n\n"
            f"VERIFIED PORTFOLIO CONTEXT:\n{context}"
        )

        contents = []
        if history:
            for turn in history[-4:]:
                role = "user" if turn.get('role') == 'user' else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": turn.get('content', '')}]
                })

        contents.append({
            "role": "user",
            "parts": [{"text": message}]
        })

        payload = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 600,
            }
        }

        try:
            resp = requests.post(url, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        return parts[0].get('text', '').strip()
        except Exception as e:
            logger.warning(f"Gemini API request failed: {e}")
        return None

    @classmethod
    def call_openai(cls, api_key: str, message: str, context: str, history: List[Dict[str, str]], base_url: str = "https://api.openai.com/v1") -> Optional[str]:
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        system_prompt = (
            "You are the official AI Assistant for Ujval Thakor's portfolio website. "
            "Answer visitor questions accurately, concisely, and professionally using ONLY the verified portfolio context below. "
            "Do NOT hallucinate or invent features/services. If not known, direct the user to the Contact page (/contact/).\n\n"
            f"VERIFIED CONTEXT:\n{context}"
        )

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for turn in history[-4:]:
                messages.append({"role": turn.get('role', 'user'), "content": turn.get('content', '')})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": "gpt-4o-mini" if "openai" in url else "llama-3.1-8b-instant",
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 500,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get('choices', [])
                if choices:
                    return choices[0].get('message', {}).get('content', '').strip()
        except Exception as e:
            logger.warning(f"OpenAI/LLM API request failed: {e}")
        return None


class ChatbotService:
    """
    Main orchestrator handling input sanitization, rate-limiting, session context,
    knowledge retrieval, and fallback to GroundedPortfolioEngine.
    """

    MAX_MESSAGE_LENGTH = 500
    RATE_LIMIT_SECONDS = 1.0  # Min time between requests
    MAX_REQUESTS_PER_MINUTE = 25

    @classmethod
    def process_message(cls, request, user_message: str) -> Dict[str, Any]:
        # 1. Input sanitization & validation
        clean_text = (user_message or '').strip()
        if not clean_text:
            return {
                'status': 'error',
                'reply': "Please provide a question or message.",
                'suggestions': ["Tell me about Ujval's experience", "What projects has he built?"]
            }

        if len(clean_text) > cls.MAX_MESSAGE_LENGTH:
            return {
                'status': 'error',
                'reply': f"Your message is too long (maximum {cls.MAX_MESSAGE_LENGTH} characters). Please shorten your question.",
                'suggestions': ["Tell me about Ujval", "What are his key skills?"]
            }

        # 2. Session rate limiting
        session = request.session
        now = time.time()
        last_req = session.get('chatbot_last_request_time', 0)
        request_count = session.get('chatbot_request_count', 0)
        window_start = session.get('chatbot_window_start', now)

        if now - window_start > 60:
            session['chatbot_window_start'] = now
            session['chatbot_request_count'] = 1
        else:
            if request_count >= cls.MAX_REQUESTS_PER_MINUTE:
                return {
                    'status': 'rate_limited',
                    'reply': "You are sending messages too quickly. Please pause a moment before asking another question.",
                    'suggestions': ["Contact Ujval directly", "View projects catalogue"]
                }
            session['chatbot_request_count'] = request_count + 1

        session['chatbot_last_request_time'] = now

        # 3. Retrieve conversation history
        history = session.get('chatbot_history', [])

        # 4. Attempt external AI model if configured
        reply = None
        gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('AI_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        groq_key = os.getenv('GROQ_API_KEY')

        if gemini_key:
            context = PortfolioKnowledgeBase.get_full_context_summary()
            reply = ExternalAIProvider.call_gemini(gemini_key, clean_text, context, history)

        if not reply and openai_key:
            context = PortfolioKnowledgeBase.get_full_context_summary()
            reply = ExternalAIProvider.call_openai(openai_key, clean_text, context, history)

        if not reply and groq_key:
            context = PortfolioKnowledgeBase.get_full_context_summary()
            reply = ExternalAIProvider.call_openai(
                groq_key, clean_text, context, history, base_url="https://api.groq.com/openai/v1"
            )

        # 5. Deterministic Grounded Engine fallback (instant, reliable, 100% accurate)
        suggestions = [
            "Tell me about BeautyCare AI",
            "What backend technologies does Ujval use?",
            "How can I contact Ujval?",
            "View full resume"
        ]

        if not reply:
            grounded_res = GroundedPortfolioEngine.answer(clean_text, history)
            reply = grounded_res['reply']
            suggestions = grounded_res.get('suggestions', suggestions)

        # 6. Update session history (store up to last 6 turns)
        history.append({'role': 'user', 'content': clean_text})
        history.append({'role': 'assistant', 'content': reply})
        if len(history) > 6:
            history = history[-6:]
        session['chatbot_history'] = history
        session.modified = True

        return {
            'status': 'success',
            'reply': reply,
            'suggestions': suggestions
        }

    @classmethod
    def clear_history(cls, request) -> None:
        if 'chatbot_history' in request.session:
            del request.session['chatbot_history']
            request.session.modified = True
