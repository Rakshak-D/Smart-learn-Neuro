from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Lesson, LessonProgress
from .serializers import LessonSerializer, LessonProgressSerializer

@login_required
def lesson_list(request):
    """
    Display a list of all lessons.
    User must be logged in.
    """
    lessons = Lesson.objects.all()
    return render(request, 'lessons/lesson_list.html', {'lessons': lessons})

@login_required
def lesson_detail(request, pk):
    """
    Display details of a specific lesson.
    Retrieves or creates progress for the current user.
    Splits content into chunks if user prefers.
    """
    lesson = get_object_or_404(Lesson, pk=pk)
    progress, created = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    chunks = lesson.get_chunks()
    return render(request, 'lessons/lesson_detail.html', {
        'lesson': lesson,
        'progress': progress,
        'chunks': chunks,
    })

@login_required
def lesson_download(request, pk):
    """
    Provide lesson content as a downloadable text file.
    """
    lesson = get_object_or_404(Lesson, pk=pk)
    response = HttpResponse(lesson.content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{lesson.title}.txt"'
    return response

class LessonViewSet(viewsets.ModelViewSet):
    """
    API endpoint to view or edit lessons.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint to view or edit lesson progress.
    """
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
