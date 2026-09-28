from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AvailabilityStatus,
    Conversation,
    Message,
    Lead,
    Notification,
    AgentConfiguration
)


@admin.register(AvailabilityStatus)
class AvailabilityStatusAdmin(admin.ModelAdmin):
    list_display = ('status_badge', 'headline', 'project_work', 'freelance', 'full_time', 'internship', 'last_updated')
    list_editable = ('project_work', 'freelance', 'full_time', 'internship')
    fieldsets = (
        ('Status Setting', {
            'fields': ('status', 'headline')
        }),
        ('Work Types Accepted', {
            'fields': ('project_work', 'freelance', 'full_time', 'internship')
        }),
        ('Notes for AI Assistant', {
            'fields': ('notes',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'AVAILABLE': '#10b981',
            'LIMITED': '#f59e0b',
            'UNAVAILABLE': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Current Status'

    def has_add_permission(self, request):
        if AvailabilityStatus.objects.exists():
            return False
        return True


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('role', 'content', 'metadata', 'timestamp')
    can_delete = False
    ordering = ('timestamp',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_short', 'detected_intent_badge', 'lead_score_badge', 'status', 'handoff_requested', 'created_at')
    list_filter = ('status', 'detected_intent', 'lead_temperature', 'handoff_requested', 'created_at')
    search_fields = ('session_key', 'visitor_ip', 'user_agent')
    readonly_fields = ('session_key', 'visitor_ip', 'user_agent', 'created_at', 'updated_at')
    inlines = [MessageInline]

    def session_short(self, obj):
        return obj.session_key[:12] + '...' if len(obj.session_key) > 12 else obj.session_key
    session_short.short_description = 'Session'

    def detected_intent_badge(self, obj):
        colors = {
            'potential_client': '#ff5d1f',
            'recruiter': '#3b82f6',
            'developer': '#8b5cf6',
            'student': '#10b981',
            'general_visitor': '#64748b',
        }
        color = colors.get(obj.detected_intent, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_detected_intent_display()
        )
    detected_intent_badge.short_description = 'Detected Intent'

    def lead_score_badge(self, obj):
        if obj.lead_score >= 75:
            color = '#ef4444'
            badge = f"🔥 {obj.lead_score} (HOT)"
        elif obj.lead_score >= 40:
            color = '#f59e0b'
            badge = f"⚡ {obj.lead_score} (WARM)"
        else:
            color = '#64748b'
            badge = f"{obj.lead_score} (COLD)"
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 12px;">{}</span>',
            color,
            badge
        )
    lead_score_badge.short_description = 'Score'


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name_or_id', 'email', 'company', 'lead_type_badge', 'temperature_badge', 'score', 'status', 'notified', 'created_at')
    list_filter = ('status', 'temperature', 'lead_type', 'notified', 'created_at')
    search_fields = ('name', 'email', 'company', 'requirements', 'intent')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'notified_at')

    fieldsets = (
        ('Lead Identity', {
            'fields': ('name', 'email', 'company', 'preferred_contact')
        }),
        ('Classification & Scoring', {
            'fields': ('lead_type', 'intent', 'score', 'temperature', 'status', 'conversation')
        }),
        ('Project Requirements', {
            'fields': ('project_type', 'requirements', 'budget_range', 'timeline')
        }),
        ('Notification Status', {
            'fields': ('notified', 'notified_at')
        }),
    )

    def name_or_id(self, obj):
        return obj.name or f"Lead #{obj.id} ({obj.company or 'Anonymous'})"
    name_or_id.short_description = 'Lead'

    def lead_type_badge(self, obj):
        colors = {
            'potential_client': '#ff5d1f',
            'recruiter': '#3b82f6',
            'developer': '#8b5cf6',
            'student': '#10b981',
            'general_visitor': '#64748b',
        }
        color = colors.get(obj.lead_type, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 2px 7px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_lead_type_display()
        )
    lead_type_badge.short_description = 'Type'

    def temperature_badge(self, obj):
        if obj.temperature == 'hot':
            return format_html('<span style="color: #ef4444; font-weight: bold;">🔥 HOT</span>')
        elif obj.temperature == 'warm':
            return format_html('<span style="color: #f59e0b; font-weight: bold;">🟡 WARM</span>')
        return format_html('<span style="color: #64748b;">❄️ COLD</span>')
    temperature_badge.short_description = 'Temp'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead_link', 'channel', 'status_badge', 'recipient', 'subject', 'sent_at')
    list_filter = ('channel', 'status', 'sent_at')
    search_fields = ('recipient', 'subject', 'payload_preview', 'error_message')
    readonly_fields = ('sent_at',)

    def lead_link(self, obj):
        return f"{obj.lead.name or 'Lead'} (#{obj.lead_id})"
    lead_link.short_description = 'Lead'

    def status_badge(self, obj):
        colors = {'sent': '#10b981', 'pending': '#f59e0b', 'failed': '#ef4444'}
        color = colors.get(obj.status, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(AgentConfiguration)
class AgentConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'active_provider', 'hot_lead_threshold', 'notification_email', 'email_notifications_enabled')
    fieldsets = (
        ('General Configuration', {
            'fields': ('name', 'headline', 'active_provider')
        }),
        ('Notification Rules', {
            'fields': ('hot_lead_threshold', 'notification_email', 'email_notifications_enabled')
        }),
        ('Pricing & Quoting Policy', {
            'fields': ('pricing_disclosed', 'pricing_notes')
        }),
        ('Prompt Customization', {
            'fields': ('custom_instructions',)
        }),
    )

    def has_add_permission(self, request):
        if AgentConfiguration.objects.exists():
            return False
        return True
