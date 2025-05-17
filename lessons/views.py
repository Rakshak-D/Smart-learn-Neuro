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
    """
    lessons = Lesson.objects.all()
    return render(request, 'lessons/lesson_list.html', {'lessons': lessons})


@login_required
def lesson_detail(request, pk):
    """
    Display a specific lesson with content chunks and navigation.
    """
    lesson = get_object_or_404(Lesson, pk=pk)
    progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    chunks = lesson.get_chunks(request.user)

    # Navigation logic
    lessons = list(Lesson.objects.order_by('id'))
    current_index = next((i for i, l in enumerate(lessons) if l.id == lesson.id), None)
    prev_lesson = lessons[current_index - 1] if current_index > 0 else None
    next_lesson = lessons[current_index + 1] if current_index is not None and current_index + 1 < len(lessons) else None

    return render(request, 'lessons/lesson_detail.html', {
        'lesson': lesson,
        'progress': progress,
        'chunks': chunks,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
    })


@login_required
def lesson_download(request, pk):
    """
    Provide lesson content as a downloadable .txt file.
    """
    lesson = get_object_or_404(Lesson, pk=pk)
    response = HttpResponse(lesson.content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{lesson.title}.txt"'
    return response


# API Views using Django REST Framework

class LessonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on lessons.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on lesson progress.
    """
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
