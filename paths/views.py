from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import LearningPath, UserPath
from .serializers import LearningPathSerializer, UserPathSerializer
import json

@login_required
def path_list(request):
    paths = LearningPath.objects.all()
    user_paths = UserPath.objects.filter(user=request.user)
    return render(request, 'paths/path_list.html', {'paths': paths, 'user_paths': user_paths})

@login_required
def path_detail(request, pk):
    path = get_object_or_404(LearningPath, pk=pk)
    user_path, created = UserPath.objects.get_or_create(user=request.user, path=path)

    if request.method == 'POST':
        customized_order = request.POST.get('customized_order')
        try:
            order = json.loads(customized_order) if customized_order else []
            # Validate lesson IDs
            valid_ids = path.lessons.values_list('id', flat=True)
            if all(isinstance(i, int) and i in valid_ids for i in order):
                user_path.customized_order = order
                user_path.save()
                return redirect('path_list')
            else:
                messages.error(request, "Invalid lesson IDs in customized order.")
        except json.JSONDecodeError:
            messages.error(request, "Invalid JSON format for customized order.")
    
    return render(request, 'paths/path_detail.html', {'path': path, 'user_path': user_path})

class LearningPathViewSet(viewsets.ModelViewSet):
    queryset = LearningPath.objects.all()
    serializer_class = LearningPathSerializer

class UserPathViewSet(viewsets.ModelViewSet):
    queryset = UserPath.objects.all()
    serializer_class = UserPathSerializer