from django.db import models
from django.utils.text import slugify

class Technology(models.Model):
    CATEGORY_CHOICES = [
        ('BACKEND', 'Backend'),
        ('DATABASE', 'Database'),
        ('TOOLS', 'Tools & Environment'),
        ('AI_CV', 'AI & Computer Vision'),
        ('DEVOPS', 'DevOps & Deployment'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='BACKEND')
    icon = models.CharField(max_length=100, blank=True, help_text="Lucide icon name or SVG descriptor")
    description = models.CharField(max_length=255, blank=True, help_text="Concise engineering role of this tech")
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Technology'
        verbose_name_plural = 'Technologies'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    project_number = models.CharField(max_length=10, default="01", help_text="e.g. 01, 02")
    category = models.CharField(max_length=100, help_text="e.g. AI & REST APIs, Computer Vision, Backend System")
    year = models.CharField(max_length=20, default="2026")
    short_description = models.TextField(help_text="One or two crisp sentences for cards and summaries")
    description = models.TextField(help_text="In-depth project case study and overview")
    featured = models.BooleanField(default=True)
    
    github_url = models.URLField(blank=True, default="", help_text="GitHub repository URL")
    live_url = models.URLField(blank=True, default="", help_text="Live demo or swagger endpoint URL")
    
    # Deep Case Study Engineering Fields
    architecture_description = models.TextField(blank=True, help_text="Detailed engineering architecture breakdown")
    architecture_flow = models.TextField(blank=True, help_text="Semicolon or newline separated pipeline stages")
    challenge = models.TextField(blank=True, help_text="Real technical challenge encountered")
    solution = models.TextField(blank=True, help_text="Exact engineered solution and design pattern used")
    learning = models.TextField(blank=True, help_text="Key takeaways and architectural insights")
    key_features = models.TextField(blank=True, help_text="Key technical features, newline separated")
    
    technologies = models.ManyToManyField(Technology, related_name='projects', blank=True)
    thumbnail = models.ImageField(upload_to='projects/thumbnails/', blank=True, null=True)
    thumbnail_svg_code = models.TextField(blank=True, help_text="Inline technical SVG visual or schematic diagram")
    
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_features_list(self):
        if not self.key_features:
            return []
        return [f.strip() for f in self.key_features.split('\n') if f.strip()]

    def get_flow_stages(self):
        if not self.architecture_flow:
            return []
        # Support newline or arrow or semicolon separated flow
        raw = self.architecture_flow.replace('↓', '\n').replace('->', '\n').replace(';', '\n')
        return [stage.strip() for stage in raw.split('\n') if stage.strip()]

    def __str__(self):
        return f"{self.project_number} — {self.title}"


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/gallery/', blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, help_text="Fallback external URL or static path")
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Project Image'
        verbose_name_plural = 'Project Images'

    def __str__(self):
        return f"Image for {self.project.title} (#{self.order})"
