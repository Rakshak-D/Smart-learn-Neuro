from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import process_gesture
import numpy as np

@csrf_exempt
def process_gesture_view(request):
    if request.method == 'POST':
        try:
            data = request.json()
            frame_data = np.array(data['frame'], dtype=np.uint8)
            # Reshape frame (assuming 4 channels: RGBA)
            height, width = 480, 640  # Adjust based on client
            frame = frame_data.reshape((height, width, 4))
            gesture = process_gesture(frame)
            return JsonResponse({'gesture': gesture})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)