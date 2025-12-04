from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
import traceback
# from .rag_pipeline import get_chatbot_response
from .rag_pipeline_groq import get_chatbot_response  # <--- Dùng dòng này khi Demo

@require_POST
def chatbot_api(request):
    try:
        # Lấy dữ liệu JSON từ body của request
        data = json.loads(request.body)
        question = data.get('question')
        
        print(f"Nhận câu hỏi: {question}") # <--- In ra để kiểm tra xem server có nhận được câu hỏi không

        if not question:
            return JsonResponse({'error': 'Missing question'}, status=400)
        
        # Gọi bộ não AI
        answer = get_chatbot_response(question)
        
        return JsonResponse({'answer': answer})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        # --- QUAN TRỌNG: In lỗi chi tiết ra terminal ---
        print("======== LỖI SERVER 500 ========")
        traceback.print_exc() 
        print(f"Chi tiết lỗi: {str(e)}")
        # ----------------------------------------------
        return JsonResponse({'error': str(e)}, status=500)