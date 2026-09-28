#import models
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie

from .services import ChatbotService, PortfolioKnowledgeBase
from .knowledge_base import CentralKnowledgeBase
from .lead_engine import LeadEngine


@require_POST
def chat_message_view(request):
    """
    Primary endpoint for processing user chat queries.
    Accepts JSON body `{"message": "..."}` or POST form data `message`.
    """
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
            user_message = data.get('message', '')
        else:
            user_message = request.POST.get('message', '')
    except Exception:
        return JsonResponse({
            'status': 'error',
            'reply': "Invalid request format. Please send a valid message string.",
            'suggestions': []
        }, status=400)

    result = ChatbotService.process_message(request, user_message)
    return JsonResponse(result)


@require_POST
def chat_clear_view(request):
    """
    Clears the active session chat history.
    """
    ChatbotService.clear_history(request)
    return JsonResponse({'status': 'cleared', 'message': 'Chat session history cleared.'})


@require_GET
def chat_suggestions_view(request):
    """
    Returns initial suggestion prompts based on the current portfolio projects and live availability.
    """
    avail = CentralKnowledgeBase.get_availability()
    avail_status = "Available for projects" if avail.get('is_available') else "Check availability"

    suggestions = [
        "Is Ujval available for projects?",
        "What can Ujval build for my company?",
        "Tell me about the Fabric Fault Detection project",
        "Tell me about BeautyCare AI",
        "What backend technologies does Ujval specialize in?",
        "I want to hire Ujval",
    ]
    return JsonResponse({'suggestions': suggestions, 'availability': avail})


@require_GET
def chat_availability_view(request):
    """
    Public live availability status endpoint read directly by UI widgets.
    """
    avail = CentralKnowledgeBase.get_availability()
    return JsonResponse(avail)


@require_POST
def chat_handoff_view(request):
    """
    Explicit human handoff endpoint triggered when user clicks 'Talk to Ujval' or submits lead contact info.
    """
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()
    except Exception:
        data = {}

    conv = ChatbotService.get_or_create_conversation(request)
    lead = LeadEngine.trigger_human_handoff(conv, data)

    return JsonResponse({
        'status': 'success',
        'message': "Thank you! Your inquiry and context have been forwarded directly to Ujval's inbox.",
        'lead_id': lead.id,
        'handoff_requested': True
    })
