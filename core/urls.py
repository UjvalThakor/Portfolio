from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('resume/', views.resume_view, name='resume_view'),
    path('resume/download/', views.resume_download, name='resume_download'),
    path('api/v1/health/', views.api_health, name='api_health'),
    path('api/v1/projects/', views.api_projects, name='api_projects'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
]
