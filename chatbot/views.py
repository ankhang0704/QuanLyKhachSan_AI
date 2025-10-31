from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from .rag_pipeline import get_chatbot_response


# Create your views here.
@require_POST
def chatbot_api(request):
    try:
        # Lấy dữ liệu JSON từ body của request
        data = json.loads(request.body)
        question = data.get('question')
        
        if not question:
            return JsonResponse({'error': 'Missing question'}, status=400)
        
        # Gọi bộ não AI
        answer = get_chatbot_response(question)
        
        return JsonResponse({'answer': answer})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)