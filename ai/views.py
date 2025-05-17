from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .recommendation.recommendation import recommend_lessons

class RecommendationView(APIView):
    def get(self, request):
        user_id = request.user.id
        lessons = [{'id': 1, 'title': 'Lesson 1'}, {'id': 2, 'title': 'Lesson 2'}]
        recommended = recommend_lessons(user_id, lessons)
        return Response(recommended)
