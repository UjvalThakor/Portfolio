from django.contrib import admin
from django.utils.html import format_html
from .models import Technology, Project, ProjectImage

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'image_url', 'caption', 'order')

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_number', 'title', 'category', 'year', 'featured', 'order', 'github_link', 'live_link')
    list_filter = ('featured', 'category', 'year')
    search_fields = ('title', 'short_description', 'description', 'architecture_description')
    list_editable = ('order', 'featured')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('technologies',)
    inlines = [ProjectImageInline]
    ordering = ('order', '-created_at')

    fieldsets = (
        ('Header & Identity', {
            'fields': ('project_number', 'title', 'slug', 'category', 'year', 'featured', 'order')
        }),
        ('Narrative & Summaries', {
            'fields': ('short_description', 'description')
        }),
        ('Links & Visuals', {
            'fields': ('github_url', 'live_url', 'thumbnail', 'thumbnail_svg_code')
        }),
        ('Deep Technical Architecture & Case Study', {
            'classes': ('collapse',),
            'fields': ('architecture_description', 'architecture_flow', 'challenge', 'solution', 'learning', 'key_features')
        }),
        ('Associated Technologies', {
            'fields': ('technologies',)
        }),
    )

    def github_link(self, obj):
        if obj.github_url:
            return format_html('<a href="{}" target="_blank" rel="noopener">Repo</a>', obj.github_url)
        return "-"
    github_link.short_description = "GitHub"

    def live_link(self, obj):
        if obj.live_url:
            return format_html('<a href="{}" target="_blank" rel="noopener">Live</a>', obj.live_url)
        return "-"
    live_link.short_description = "Live Demo"

@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ('project', 'caption', 'order')
    list_filter = ('project',)
    list_editable = ('order',)
