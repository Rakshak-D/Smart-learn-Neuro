from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import (
    Assessment, AssessmentQuestion, AssessmentResult,
    LearningTask, TaskPerformance, AdaptiveLearningProfile
)
from .utils import AdaptiveLearningEngine, TextToSpeechConverter
from .recommendation.recommendation import recommend_lessons
from lessons.models import Lesson
from users.models import CustomUser

User = get_user_model()

class RecommendationView(APIView):
    """View for getting personalized lesson recommendations"""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        user = request.user
        adaptive_engine = AdaptiveLearningEngine(user)
        
        # Get recommended lessons based on user's learning style and performance
        recommended_lessons = adaptive_engine.get_personalized_lessons()
        
        return Response({
            'lessons': recommended_lessons,
            'learning_style': user.learning_style,
            'engagement_level': user.engagement_level
        })

@csrf_exempt
def process_gesture_view(request):
    """Process user gestures for interaction"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            gesture = data.get('gesture')
            user = request.user
            
            # Process gesture and get response
            response = TextToSpeechConverter.process_gesture(gesture, user)
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return JsonResponse({'error': 'POST request required'}, status=status.HTTP_400_BAD_REQUEST)

class AssessmentView(APIView):
    """View for handling assessments"""
    def get(self, request):
        """Get assessment for user based on their learning condition"""
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        # Get appropriate assessment type based on learning condition
        assessment_type = user.learning_condition
        
        # Get or create assessment
        assessment = Assessment.objects.filter(
            type=assessment_type,
            topic__subject='English'
        ).first()
        
        if not assessment:
            return Response({'error': 'No assessment found'}, status=status.HTTP_404_NOT_FOUND)
            
        questions = AssessmentQuestion.objects.filter(assessment=assessment)
        
        return Response({
            'assessment': {
                'id': assessment.id,
                'name': assessment.name,
                'type': assessment.type,
                'questions': [
                    {
                        'id': q.id,
                        'question': q.question_text,
                        'type': q.type,
                        'options': q.options
                    } for q in questions
                ]
            }
        })

    def post(self, request):
        """Submit assessment results and get feedback"""
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            data = request.data
            assessment_id = data.get('assessment_id')
            answers = data.get('answers')
            
            assessment = get_object_or_404(Assessment, id=assessment_id)
            questions = AssessmentQuestion.objects.filter(assessment=assessment)
            
            # Calculate score
            score = 0
            feedback = []
            for q in questions:
                user_answer = answers.get(str(q.id))
                if user_answer == q.correct_answer:
                    score += 1
                else:
                    feedback.append({
                        'question': q.question_text,
                        'correct_answer': q.correct_answer,
                        'user_answer': user_answer
                    })
            
            score = (score / len(questions)) * 100
            
            # Save assessment result
            AssessmentResult.objects.create(
                user=user,
                assessment=assessment,
                score=score,
                answers=answers,
                feedback=json.dumps(feedback)
            )
            
            # Update adaptive learning profile
            adaptive_profile = AdaptiveLearningProfile.objects.get_or_create(user=user)[0]
            adaptive_profile.engagement_level = score / 100
            adaptive_profile.save()
            
            return Response({
                'score': score,
                'feedback': feedback,
                'recommendations': adaptive_profile.get_recommendations()
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def text_to_speech_view(request):
    """Convert text to speech for dyslexia support"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')
            user = request.user
            
            # Convert text to speech with personalized settings
            audio = TextToSpeechConverter.convert(text, user)
            
            return JsonResponse({
                'audio_url': audio.url,
                'duration': audio.duration
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return JsonResponse({'error': 'POST request required'}, status=status.HTTP_400_BAD_REQUEST)

class AdaptiveLearningView(APIView):
    """View for adaptive learning"""
    def get(self, request):
        """Get adaptive learning recommendations"""
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        adaptive_profile = get_object_or_404(AdaptiveLearningProfile, user=user)
        
        return Response({
            'learning_style': adaptive_profile.learning_style,
            'engagement_level': adaptive_profile.engagement_level,
            'preferred_pace': adaptive_profile.preferred_pace,
            'next_assessment_due': adaptive_profile.next_assessment_due
        })

    def post(self, request):
        """Update adaptive learning profile"""
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            data = request.data
            adaptive_profile = AdaptiveLearningProfile.objects.get_or_create(user=user)[0]
            
            if 'learning_style' in data:
                adaptive_profile.learning_style = data['learning_style']
            if 'engagement_level' in data:
                adaptive_profile.engagement_level = data['engagement_level']
            if 'preferred_pace' in data:
                adaptive_profile.preferred_pace = data['preferred_pace']
            
            adaptive_profile.save()
            
            return Response({
                'message': 'Adaptive profile updated successfully',
                'profile': {
                    'learning_style': adaptive_profile.learning_style,
                    'engagement_level': adaptive_profile.engagement_level,
                    'preferred_pace': adaptive_profile.preferred_pace
                }
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
