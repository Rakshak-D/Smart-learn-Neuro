from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import LearningPath, UserPath
from .serializers import LearningPathSerializer, UserPathSerializer

@login_required
def path_list(request):
    # Get all learning paths and user's customized paths
    paths = LearningPath.objects.all()
    user_paths = UserPath.objects.filter(user=request.user)
    return render(request, 'paths/path_list.html', {'paths': paths, 'user_paths': user_paths})

@login_required
def path_detail(request, pk):
    # Get the specific learning path or 404
    path = get_object_or_404(LearningPath, pk=pk)
    # Get or create user's customized path
    user_path, created = UserPath.objects.get_or_create(user=request.user, path=path)

    if request.method == 'POST':
        # Save customized lesson order submitted by user
        customized_order = request.POST.get('customized_order')
        user_path.customized_order = customized_order
        user_path.save()
        return redirect('path_list')

    return render(request, 'paths/path_detail.html', {'path': path, 'user_path': user_path})

class LearningPathViewSet(viewsets.ModelViewSet):
    queryset = LearningPath.objects.all()
    serializer_class = LearningPathSerializer

class UserPathViewSet(viewsets.ModelViewSet):
    queryset = UserPath.objects.all()
    serializer_class = UserPathSerializer
