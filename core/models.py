from django.db import models

class Experience(models.Model):
    TYPE_CHOICES = [
        ('INTERNSHIP', 'Internship'),
        ('PROFESSIONAL_PROJECT', 'Professional Project'),
        ('PERSONAL_PROJECT', 'Personal Project'),
    ]

    company = models.CharField(max_length=200, help_text="Organization, company or independent project scope")
    role = models.CharField(max_length=200, help_text="Role e.g. Python Backend Developer / AI-CV Intern")
    location = models.CharField(max_length=150, default="Surat, Gujarat, India")
    description = models.TextField(help_text="Overview of responsibilities and technical engineering scope")
    highlights = models.TextField(blank=True, help_text="Newline-separated bullet points of technical achievements")
    start_date = models.CharField(max_length=50, help_text="e.g. Jan 2024")
    end_date = models.CharField(max_length=50, default="Present", help_text="e.g. Present or June 2024")
    is_current = models.BooleanField(default=False)
    experience_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='PERSONAL_PROJECT')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = 'Experience'
        verbose_name_plural = 'Experiences'

    def get_highlights_list(self):
        if not self.highlights:
            return []
        return [h.strip() for h in self.highlights.split('\n') if h.strip()]

    def __str__(self):
        return f"{self.role} at {self.company} ({self.get_experience_type_display()})"


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('BACKEND', 'Backend & Core'),
        ('DATABASE', 'Database & Caching'),
        ('ARCHITECTURE', 'System Architecture & APIs'),
        ('AI_CV', 'AI & Computer Vision'),
        ('DEVOPS', 'DevOps & Tooling'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='BACKEND')
    badge_label = models.CharField(max_length=50, blank=True, help_text="e.g. Production Ready, Core Strength, Hands-on")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'order', 'name']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

    def __str__(self):
        return f"{self.name} [{self.get_category_display()}]"


class Resume(models.Model):
    title = models.CharField(max_length=200, default="Ujval Thakor — Backend Developer Resume")
    file = models.FileField(upload_to='resumes/', blank=True, null=True)
    summary = models.TextField(blank=True, default="B.Tech Computer Engineering student with hands-on Python and Django development experience. Skilled in REST APIs, MySQL, PostgreSQL, Redis, Docker, OpenCV, and AI integration.")
    uploaded_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Only one resume should be active at a time")
    download_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Resume'
        verbose_name_plural = 'Resumes'

    def save(self, *args, **kwargs):
        if self.is_active:
            # Mark all others as inactive
            Resume.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({'Active' if self.is_active else 'Inactive'})"


class ProfileConfig(models.Model):
    """
    Editable developer profile config via Django Admin
    ensuring no hardcoded personal data in templates.
    """
    full_name = models.CharField(max_length=100, default="Ujval Thakor")
    primary_title = models.CharField(max_length=100, default="Backend Developer")
    secondary_title = models.CharField(max_length=150, default="Python • Django • REST APIs • AI/ML")
    short_positioning = models.TextField(
        default="I build reliable backend systems, APIs, automation tools, and AI-powered applications."
    )
    current_status = models.CharField(
        max_length=200,
        default="B.Tech Computer Engineering student with hands-on Python and Django development experience."
    )
    location = models.CharField(max_length=100, default="Surat, Gujarat, India")
    available_for_work = models.BooleanField(default=True)
    
    github_url = models.URLField(blank=True, default="https://github.com/ujvalthakor")
    linkedin_url = models.URLField(blank=True, default="https://linkedin.com/in/ujvalthakor")
    email = models.EmailField(default="ujvalthakor14@gmail.com")
    
    hero_statement_line1 = models.CharField(max_length=100, default="BACKEND")
    hero_statement_line2 = models.CharField(max_length=100, default="ENGINEER")
    hero_statement_line3 = models.CharField(max_length=100, default="who builds")
    hero_statement_line4 = models.CharField(max_length=100, default="systems that")
    hero_statement_line5 = models.CharField(max_length=100, default="actually work.")

    about_editorial_heading = models.TextField(
        default="I BUILD THE\nSYSTEM BEHIND\nTHE EXPERIENCE."
    )
    about_editorial_text = models.TextField(
        default="I’m a B.Tech Computer Engineering student and backend developer focused on Python and Django. I enjoy turning ideas into structured backend systems — from REST APIs and database architecture to authentication, automation and AI-powered applications."
    )

    class Meta:
        verbose_name = 'Profile Configuration'
        verbose_name_plural = 'Profile Configuration'

    def __str__(self):
        return f"{self.full_name} Profile Settings"
