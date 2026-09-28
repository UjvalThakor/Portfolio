#import models
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie

from .services import ChatbotService, PortfolioKnowledgeBase

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
    Returns initial suggestion prompts based on the current portfolio projects.
    """
    projects = PortfolioKnowledgeBase.get_projects()
    top_project = projects[0]['title'] if projects else "BeautyCare AI"

    suggestions = [
        "What backend technologies does Ujval specialize in?",
        f"Tell me about the {top_project} project",
        "What is Ujval's academic background?",
        "How can I get in touch with Ujval?",
    ]
    return JsonResponse({'suggestions': suggestions})
