from django.contrib import admin
from django.utils.html import format_html
from .models import Experience, Skill, Resume, ProfileConfig

@admin.register(ProfileConfig)
class ProfileConfigAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'primary_title', 'location', 'available_for_work')
    fieldsets = (
        ('Basic Information', {
            'fields': ('full_name', 'primary_title', 'secondary_title', 'location', 'available_for_work')
        }),
        ('Positions & Bio', {
            'fields': ('short_positioning', 'current_status')
        }),
        ('Links', {
            'fields': ('github_url', 'linkedin_url', 'email')
        }),
        ('Hero Statement Blocks', {
            'fields': (
                'hero_statement_line1',
                'hero_statement_line2',
                'hero_statement_line3',
                'hero_statement_line4',
                'hero_statement_line5'
            )
        }),
        ('About Editorial Section', {
            'fields': ('about_editorial_heading', 'about_editorial_text')
        }),
    )

    def has_add_permission(self, request):
        # Allow at most one config object
        if ProfileConfig.objects.exists():
            return False
        return True

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('role', 'company', 'experience_type', 'start_date', 'end_date', 'order')
    list_filter = ('experience_type', 'is_current')
    search_fields = ('company', 'role', 'description')
    list_editable = ('order',)
    ordering = ('order', '-id')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'badge_label', 'order')
    list_filter = ('category',)
    search_fields = ('name',)
    list_editable = ('order',)
    ordering = ('category', 'order', 'name')

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'is_active', 'download_count', 'file_link')
    list_editable = ('is_active',)

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Download File</a>', obj.file.url)
        return "No file uploaded (uses dynamic generated CV)"
    file_link.short_description = "File"
