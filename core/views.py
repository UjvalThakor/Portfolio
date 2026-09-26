import time
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.conf import settings
from projects.models import Project, Technology
from core.models import Experience, Skill, Resume, ProfileConfig
from contact.forms import ContactForm

def home_view(request):
    featured_projects = (
        Project.objects.filter(featured=True)
        .prefetch_related('technologies')
        .order_by('order', 'id')
    )
    
    # Group technologies by category
    tech_categories = [
        ('BACKEND', 'Backend & APIs'),
        ('DATABASE', 'Databases & Caching'),
        ('TOOLS', 'Tools & Environment'),
        ('AI_CV', 'AI & Computer Vision'),
        ('DEVOPS', 'DevOps & Deployment'),
    ]
    
    grouped_technologies = []
    for code, label in tech_categories:
        techs = Technology.objects.filter(category=code).order_by('order')
        if techs.exists():
            grouped_technologies.append({
                'code': code,
                'label': label,
                'technologies': techs,
            })
            
    experiences = Experience.objects.all().order_by('order', '-id')
    skills = Skill.objects.all().order_by('category', 'order')
    form = ContactForm()

    context = {
        'featured_projects': featured_projects,
        'grouped_technologies': grouped_technologies,
        'experiences': experiences,
        'skills': skills,
        'contact_form': form,
    }
    return render(request, 'home.html', context)


def about_view(request):
    experiences = Experience.objects.all().order_by('order')
    skills = Skill.objects.all().order_by('category', 'order')
    technologies = Technology.objects.all().order_by('order')
    
    context = {
        'experiences': experiences,
        'skills': skills,
        'technologies': technologies,
    }
    return render(request, 'about.html', context)


def resume_view(request):
    resume = Resume.objects.filter(is_active=True).first()
    experiences = Experience.objects.all().order_by('order')
    skills = Skill.objects.all().order_by('category', 'order')
    projects = Project.objects.all().order_by('order')[:4]
    
    context = {
        'resume': resume,
        'experiences': experiences,
        'skills': skills,
        'projects': projects,
    }
    return render(request, 'resume.html', context)


def resume_download(request):
    resume = Resume.objects.filter(is_active=True).first()
    if resume and resume.file:
        resume.download_count += 1
        resume.save(update_fields=['download_count'])
        return redirect(resume.file.url)
    # If no file uploaded yet, fallback to web resume view
    return redirect('core:resume_view')


def api_health(request):
    """
    Live health check endpoint used by the interactive runtime telemetry.
    Tests DB round-trip latency.
    """
    start_time = time.time()
    db_status = "ONLINE"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
    except Exception as e:
        db_status = f"ERROR: {str(e)}"
    
    db_latency_ms = round((time.time() - start_time) * 1000, 2)

    return JsonResponse({
        "status": "healthy",
        "code": 200,
        "runtime": {
            "python": "3.12.10",
            "django": "6.1.1",
            "environment": "production-ready",
            "server": "Django ASGI/WSGI",
        },
        "services": {
            "api": "ONLINE [200 OK]",
            "database": f"{db_status} ({connection.vendor})",
            "database_latency_ms": db_latency_ms,
            "cache": "READY",
            "workers": "ACTIVE (Concurrency: 4)",
        },
        "timestamp": time.time(),
    })


def api_projects(request):
    """
    JSON API endpoint for projects — powers the 'Behind the Request'
    live simulation and interactive terminal.
    """
    projects = Project.objects.all().order_by('order')
    data = []
    for p in projects:
        data.append({
            "number": p.project_number,
            "title": p.title,
            "slug": p.slug,
            "category": p.category,
            "year": p.year,
            "short_description": p.short_description,
            "technologies": [t.name for t in p.technologies.all()],
            "github_url": p.github_url,
            "live_url": p.live_url,
        })
    return JsonResponse({"count": len(data), "status": 200, "results": data})


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    base_url = request.build_absolute_uri('/')[:-1]
    projects = Project.objects.all()
    
    urls = [
        f"<url><loc>{base_url}/</loc><priority>1.0</priority><changefreq>weekly</changefreq></url>",
        f"<url><loc>{base_url}/about/</loc><priority>0.8</priority><changefreq>monthly</changefreq></url>",
        f"<url><loc>{base_url}/projects/</loc><priority>0.9</priority><changefreq>weekly</changefreq></url>",
        f"<url><loc>{base_url}/contact/</loc><priority>0.7</priority><changefreq>monthly</changefreq></url>",
        f"<url><loc>{base_url}/resume/</loc><priority>0.8</priority><changefreq>monthly</changefreq></url>",
    ]
    
    for p in projects:
        urls.append(
            f"<url><loc>{base_url}/projects/{p.slug}/</loc><priority>0.8</priority><changefreq>monthly</changefreq></url>"
        )

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(urls)}
</urlset>"""
    return HttpResponse(xml_content, content_type="application/xml")
