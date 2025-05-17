import tensorflow as tf
import numpy as np
from django.db.models import Avg
from lessons.models import LessonProgress, Lesson

def recommend_lessons(user_id, lesson_data):
    """
    Recommend lessons based on user progress and preferences.
    Uses a simple collaborative filtering approach.
    """
    try:
        # Fetch user progress
        progress = LessonProgress.objects.filter(user_id=user_id).values('lesson_id', 'progress')
        completed_lessons = {p['lesson_id'] for p in progress if p['progress'] >= 80}

        # Simple scoring: prioritize uncompleted lessons with high average progress
        scores = []
        for lesson in lesson_data:
            lesson_id = lesson['id']
            if lesson_id not in completed_lessons:
                avg_progress = LessonProgress.objects.filter(lesson_id=lesson_id).aggregate(avg_progress=Avg('progress'))['avg_progress'] or 0
                scores.append((lesson, avg_progress))
        
        # Sort by score and return top 3
        scores.sort(key=lambda x: x[1], reverse=True)
        return [lesson for lesson, _ in scores[:3]]
    except Exception as e:
        print(f"Recommendation error: {e}")
        return []  # Fallback to empty list