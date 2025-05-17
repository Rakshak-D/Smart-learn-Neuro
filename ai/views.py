from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .recommendation.recommendation import recommend_lessons
from lessons.models import Lesson

class RecommendationView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=401)
        user_id = request.user.id
        lessons = [{'id': l.id, 'title': l.title} for l in Lesson.objects.all()]
        recommended = recommend_lessons(user_id, lessons)
        return Response(recommended)