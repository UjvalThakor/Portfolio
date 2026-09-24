from .models import ProfileConfig, Resume
from datetime import datetime

def portfolio_context(request):
    profile = ProfileConfig.objects.first()
    if not profile:
        profile = ProfileConfig()

    active_resume = Resume.objects.filter(is_active=True).first()

    return {
        'profile': profile,
        'active_resume': active_resume,
        'current_year': datetime.now().year,
        'django_version': '6.1',
        'python_version': '3.12',
    }
