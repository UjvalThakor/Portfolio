import re
import logging
from typing import Dict, Any, Optional, Tuple
from django.utils import timezone
from .models import Conversation, Lead, AgentConfiguration

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
PHONE_REGEX = re.compile(r'(\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9})')


class LeadEngine:
    """
    Intelligent Lead Detection, Scoring & Qualification Engine.
    Detects visitor intent, extracts key contact details conversationally,
    computes intent scores, and triggers real-time alerts for valuable leads.
    """

    @classmethod
    def detect_intent(cls, message: str, history: Optional[list] = None) -> Tuple[str, int]:
        """
        Analyzes message text and conversation context to detect intent category and baseline score.
        Returns (intent_category, baseline_intent_score).
        """
        text = message.lower()

        # 1. Potential Client Intent (Projects, Quotes, Custom Systems, Building Services)
        client_triggers = [
            'build', 'develop', 'create', 'make', 'hire you for', 'contract', 'freelance project',
            'quotation', 'quote', 'cost', 'pricing', 'estimate', 'need a developer',
            'fabric inspection', 'defect detection', 'ai system', 'computer vision system',
            'django application', 'rest api', 'my company', 'we need', 'our project',
            'have a project', 'looking for someone to build', 'client'
        ]
        if any(trig in text for trig in client_triggers):
            return ('potential_client', 45)

        # 2. Recruiter / Hiring Manager Intent
        recruiter_triggers = [
            'recruiter', 'hiring', 'job opening', 'interview', 'full time', 'permanent role',
            'salary', 'ctc', 'notice period', 'resume', 'cv', 'hire ujval', 'hire him',
            'open to work', 'join our team', 'looking for a python developer', 'backend engineer role'
        ]
        if any(trig in text for trig in recruiter_triggers):
            return ('recruiter', 40)

        # 3. Developer / Peer Inquiries
        dev_triggers = [
            'how did you build', 'architecture of', 'what library', 'redis setup',
            'multithreading', 'opencv pipeline', 'source code', 'github link', 'benchmark'
        ]
        if any(trig in text for trig in dev_triggers):
            return ('developer', 15)

        # 4. Student / Learner
        student_triggers = [
            'how to learn', 'which tutorial', 'which college', 'semester', 'student', 'guide me'
        ]
        if any(trig in text for trig in student_triggers):
            return ('student', 10)

        return ('general_visitor', 5)

    @classmethod
    def extract_contact_info(cls, message: str) -> Dict[str, str]:
        """
        Non-intrusive extraction of contact details from natural conversation.
        """
        extracted = {}

        # Email
        emails = EMAIL_REGEX.findall(message)
        if emails:
            extracted['email'] = emails[0].strip()

        # Phone
        phones = PHONE_REGEX.findall(message)
        if phones:
            valid_phones = [p for p in phones if len(re.sub(r'\D', '', p)) >= 10]
            if valid_phones:
                extracted['phone'] = valid_phones[0].strip()

        # Name extraction patterns
        name_match = re.search(r'\b(?:my name is|i am|this is|call me|i\'m)\s+([A-Za-z]+)(?:\s+([A-Za-z]+))?', message, re.IGNORECASE)
        if name_match:
            first_name = name_match.group(1).strip()
            second_name = (name_match.group(2) or '').strip()
            stop_words = {'from', 'at', 'with', 'representing', 'and', 'looking', 'interested', 'a', 'the', 'here', 'recruiter', 'working', 'an'}
            if first_name.lower() not in stop_words:
                if second_name and second_name.lower() not in stop_words:
                    extracted['name'] = f"{first_name} {second_name}"
                else:
                    extracted['name'] = first_name

        # Company extraction patterns
        company_match = re.search(r'(?i:\b(?:from|at|representing|with|we are|our company is|company is)\s+)([A-Z][A-Za-z0-9&.\s]{1,30}?)(?:\.|\,|$|\s+and|\s+we|\s+my|\s+email|\s+the\b)', message)
        if company_match:
            cand_comp = company_match.group(1).strip()
            if cand_comp.lower() not in ['a', 'the', 'my', 'our', 'looking', 'interested']:
                extracted['company'] = cand_comp

        return extracted

    @classmethod
    def calculate_score(cls, lead: Lead) -> Tuple[int, str]:
        """
        Calculates a lead quality score (0 - 100) and assigns a temperature.
        """
        score = 0

        # Base intent weights
        if lead.lead_type == 'potential_client':
            score += 40
        elif lead.lead_type == 'recruiter':
            score += 35
        elif lead.lead_type == 'developer':
            score += 15
        else:
            score += 5

        # Information richness weights
        if lead.email:
            score += 25
        if lead.name:
            score += 10
        if lead.company:
            score += 15
        if lead.requirements and len(lead.requirements) > 20:
            score += 15
        if lead.project_type:
            score += 10
        if lead.timeline or lead.budget_range:
            score += 10

        score = min(score, 100)

        # Temperature classification
        if score >= 75:
            temperature = 'hot'
        elif score >= 40:
            temperature = 'warm'
        else:
            temperature = 'cold'

        return score, temperature

    @classmethod
    def update_lead_from_data(cls, conversation: Conversation, data: Dict[str, Any]) -> Lead:
        """
        Updates or creates a Lead model linked to the conversation.
        """
        lead, created = Lead.objects.get_or_create(conversation=conversation)

        if data.get('name') and not lead.name:
            lead.name = data['name']
        if data.get('email'):
            lead.email = data['email']
        if data.get('company') and not lead.company:
            lead.company = data['company']
        if data.get('project_type'):
            lead.project_type = data['project_type']
        if data.get('requirements'):
            if lead.requirements:
                lead.requirements += f"\n{data['requirements']}"
            else:
                lead.requirements = data['requirements']
        if data.get('budget'):
            lead.budget_range = data['budget']
        if data.get('timeline'):
            lead.timeline = data['timeline']
        if data.get('lead_type'):
            lead.lead_type = data['lead_type']

        # Re-score
        score, temp = cls.calculate_score(lead)
        lead.score = score
        lead.temperature = temp
        lead.save()

        # Sync conversation
        conversation.lead_score = score
        conversation.lead_temperature = temp
        conversation.detected_intent = lead.lead_type
        if score >= 75:
            conversation.status = 'qualified'
        conversation.save()

        # Check notification trigger
        cls.evaluate_notification_trigger(lead)

        return lead

    @classmethod
    def trigger_human_handoff(cls, conversation: Conversation, data: Dict[str, Any]) -> Lead:
        """
        Explicit request to connect with Ujval directly.
        Marks conversation for human handoff and guarantees immediate notification.
        """
        conversation.handoff_requested = True
        conversation.status = 'handoff'
        conversation.save()

        lead, _ = Lead.objects.get_or_create(conversation=conversation)
        if data.get('name'):
            lead.name = data['name']
        if data.get('email'):
            lead.email = data['email']
        if data.get('note'):
            lead.requirements = (lead.requirements + f"\n[Handoff Note]: {data['note']}").strip()

        lead.score = max(lead.score, 85)
        lead.temperature = 'hot'
        lead.save()

        cls.evaluate_notification_trigger(lead, force=True)
        return lead

    @classmethod
    def evaluate_notification_trigger(cls, lead: Lead, force: bool = False) -> None:
        """
        Dispatches real-time notification to Ujval if score exceeds threshold and hasn't been notified yet.
        """
        config = AgentConfiguration.get_config()
        if not config.email_notifications_enabled and not force:
            return

        threshold = config.hot_lead_threshold
        if (lead.score >= threshold or force) and not lead.notified:
            from .notifications import NotificationDispatcher
            NotificationDispatcher.send_lead_notification(lead)
