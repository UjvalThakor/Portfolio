from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('projects/', include('projects.urls')),
    path('contact/', include('contact.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('', include('core.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "UJVAL THAKOR — Engineering Admin"
admin.site.site_title = "Backend Developer Admin"
admin.site.index_title = "Portfolio Content & System Management"
