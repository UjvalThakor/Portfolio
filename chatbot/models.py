from django.db import models
from django.utils import timezone


class AvailabilityStatus(models.Model):
    """
    Live admin-controlled availability status.
    The AI Agent checks this live state to ensure zero hallucination
    regarding Ujval's real work bandwidth.
    """
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available for Projects & Roles'),
        ('LIMITED', 'Limited Availability'),
        ('UNAVAILABLE', 'Currently Unavailable'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    headline = models.CharField(
        max_length=255,
        default="Available for selected backend, API, and AI engineering projects"
    )
    project_work = models.BooleanField(default=True, help_text="Open to freelance & contract projects")
    freelance = models.BooleanField(default=True, help_text="Open to independent consulting")
    full_time = models.BooleanField(default=True, help_text="Open to full-time engineering roles")
    internship = models.BooleanField(default=False, help_text="Open to internship roles")
    notes = models.TextField(
        blank=True,
        default="Focused on Python, Django, REST APIs, and Computer Vision / AI solutions."
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Availability Status'
        verbose_name_plural = 'Availability Status'

    def __str__(self):
        return f"{self.get_status_display()} (Updated {self.last_updated.strftime('%Y-%m-%d')})"

    @classmethod
    def get_current(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create(
                status='AVAILABLE',
                headline="Available for selected backend, API, and AI engineering projects",
                project_work=True,
                freelance=True,
                full_time=True,
                internship=False,
                notes="Focused on Python, Django, REST APIs, and Computer Vision / AI solutions."
            )
        return obj


class Conversation(models.Model):
    """
    Tracks visitor sessions, detected intent, and conversation lifecycle.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('qualified', 'Qualified Lead'),
        ('handoff', 'Human Handoff Requested'),
        ('closed', 'Closed'),
    ]

    INTENT_CHOICES = [
        ('general_visitor', 'General Visitor'),
        ('potential_client', 'Potential Client'),
        ('recruiter', 'Recruiter / Hiring Manager'),
        ('developer', 'Developer Peer'),
        ('student', 'Student / Learner'),
    ]

    TEMPERATURE_CHOICES = [
        ('cold', 'Cold (Browsing)'),
        ('warm', 'Warm (Inquiring)'),
        ('hot', 'Hot (High Intent)'),
    ]

    session_key = models.CharField(max_length=120, db_index=True)
    visitor_ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active')
    detected_intent = models.CharField(max_length=50, choices=INTENT_CHOICES, default='general_visitor')
    lead_score = models.IntegerField(default=0)
    lead_temperature = models.CharField(max_length=20, choices=TEMPERATURE_CHOICES, default='cold')
    handoff_requested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'AI Conversation'
        verbose_name_plural = 'AI Conversations'

    def __str__(self):
        return f"Conv #{self.id} [{self.get_detected_intent_display()}] — Score: {self.lead_score}"


class Message(models.Model):
    """
    Individual turn within a visitor conversation.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
        ('tool', 'Tool'),
    ]

    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f"[{self.role.upper()}] Conv #{self.conversation_id}: {self.content[:40]}..."


class Lead(models.Model):
    """
    Structured lead profile qualified progressively through conversation.
    """
    LEAD_TYPE_CHOICES = [
        ('potential_client', 'Potential Client'),
        ('recruiter', 'Recruiter / Hiring Manager'),
        ('developer', 'Developer'),
        ('student', 'Student'),
        ('general_visitor', 'General Visitor'),
    ]

    STATUS_CHOICES = [
        ('new', 'New Lead'),
        ('contacted', 'Contacted / In Progress'),
        ('qualified', 'Qualified'),
        ('closed', 'Closed / Converted'),
        ('archived', 'Archived'),
    ]

    TEMPERATURE_CHOICES = [
        ('cold', 'Cold'),
        ('warm', 'Warm'),
        ('hot', 'Hot 🔥'),
    ]

    conversation = models.OneToOneField(
        Conversation,
        related_name='lead',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    company = models.CharField(max_length=200, blank=True)
    lead_type = models.CharField(max_length=50, choices=LEAD_TYPE_CHOICES, default='potential_client')
    intent = models.CharField(max_length=255, blank=True, help_text="Summarized visitor intent")
    score = models.IntegerField(default=0, help_text="Calculated lead quality score (0 - 100)")
    temperature = models.CharField(max_length=20, choices=TEMPERATURE_CHOICES, default='cold')
    
    # Qualification details
    requirements = models.TextField(blank=True, help_text="Problem statement / requirements")
    project_type = models.CharField(max_length=150, blank=True, help_text="e.g. AI Vision, Django Backend, Automation")
    budget_range = models.CharField(max_length=100, blank=True)
    timeline = models.CharField(max_length=100, blank=True)
    preferred_contact = models.CharField(max_length=100, blank=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='new')
    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-score', '-created_at']
        verbose_name = 'Qualified Lead'
        verbose_name_plural = 'Qualified Leads'

    def __str__(self):
        title = self.name or self.company or f"Lead #{self.id}"
        return f"{title} [{self.get_lead_type_display()}] — Score: {self.score}"


class Notification(models.Model):
    """
    Log of real-time dispatches (Email, Web Push, Mobile Push).
    """
    CHANNEL_CHOICES = [
        ('email', 'Email Notification'),
        ('web_push', 'Web Push'),
        ('mobile_push', 'Mobile Push'),
        ('dashboard', 'Admin Dashboard Alert'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent Successfully'),
        ('failed', 'Failed'),
    ]

    lead = models.ForeignKey(Lead, related_name='notifications', on_delete=models.CASCADE)
    channel = models.CharField(max_length=30, choices=CHANNEL_CHOICES, default='email')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    recipient = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True)
    payload_preview = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Lead Notification'
        verbose_name_plural = 'Lead Notifications'

    def __str__(self):
        return f"{self.channel.upper()} to {self.recipient} [{self.status}]"


class AgentConfiguration(models.Model):
    """
    Control room settings for Ujval's Portfolio AI Agent.
    """
    PROVIDER_CHOICES = [
        ('auto', 'Auto-Detect (Use Available API Key)'),
        ('gemini', 'Google Gemini (Native)'),
        ('openai', 'OpenAI (GPT-4o / GPT-4o-mini)'),
        ('groq', 'Groq (Llama 3.1)'),
        ('grounded', 'Deterministic Grounded Engine (Offline/Safe)'),
    ]

    name = models.CharField(max_length=100, default="UJVAL.AI Agent")
    headline = models.CharField(max_length=255, default="Portfolio Sales & Engineering Assistant")
    active_provider = models.CharField(max_length=30, choices=PROVIDER_CHOICES, default='auto')
    hot_lead_threshold = models.IntegerField(default=75, help_text="Minimum score to trigger immediate notification")
    notification_email = models.EmailField(default="ujvalthakor14@gmail.com")
    email_notifications_enabled = models.BooleanField(default=True)
    pricing_disclosed = models.BooleanField(default=False, help_text="Allow disclosing estimated pricing if configured")
    pricing_notes = models.TextField(
        blank=True,
        default="Ujval provides custom quotes based on project specifications, timeline, and architectural requirements."
    )
    custom_instructions = models.TextField(
        blank=True,
        help_text="Optional custom instructions to append to the system prompt."
    )

    class Meta:
        verbose_name = 'Agent Configuration'
        verbose_name_plural = 'Agent Configuration'

    def __str__(self):
        return f"{self.name} Settings"

    @classmethod
    def get_config(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj
