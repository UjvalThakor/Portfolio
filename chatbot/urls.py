from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('api/message/', views.chat_message_view, name='message'),
    path('api/clear/', views.chat_clear_view, name='clear'),
    path('api/suggestions/', views.chat_suggestions_view, name='suggestions'),
    path('api/availability/', views.chat_availability_view, name='availability'),
    path('api/handoff/', views.chat_handoff_view, name='handoff'),
]
