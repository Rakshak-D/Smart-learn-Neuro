"""
Computer Vision Utilities for SmartLearn Neuro
"""
import cv2
import numpy as np
from typing import Tuple, Dict, Optional, List
import logging
import mediapipe as mp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FaceDetectionResult:
    """Container for face detection results."""
    success: bool
    face_count: int = 0
    face_locations: List[Tuple[int, int, int, int]] = None  # (top, right, bottom, left)
    landmarks: Dict[str, List[Tuple[float, float]]] = None
    error: Optional[str] = None

class FaceDetector:
    """Face detection and analysis using MediaPipe and OpenCV."""
    
    def __init__(self, model_selection=0, min_detection_confidence=0.7):
        """Initialize the face detector."""
        self.face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=model_selection,
            min_detection_confidence=min_detection_confidence
        )
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def detect_faces(self, image: np.ndarray) -> FaceDetectionResult:
        """
        Detect faces in an image.
        
        Args:
            image: Input image in BGR format
            
        Returns:
            FaceDetectionResult containing detection results
        """
        try:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            results = self.face_detection.process(image_rgb)
            
            if not results.detections:
                return FaceDetectionResult(success=True, face_count=0)
            
            # Extract face locations
            face_locations = []
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                ih, iw, _ = image.shape
                x, y, w, h = int(bbox.xmin * iw), int(bbox.ymin * ih), \
                             int(bbox.width * iw), int(bbox.height * ih)
                face_locations.append((y, x + w, y + h, x))  # (top, right, bottom, left)
            
            return FaceDetectionResult(
                success=True,
                face_count=len(face_locations),
                face_locations=face_locations
            )
            
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return FaceDetectionResult(
                success=False,
                error=str(e)
            )
    
    def detect_face_landmarks(self, image: np.ndarray) -> FaceDetectionResult:
        """
        Detect facial landmarks using MediaPipe Face Mesh.
        
        Args:
            image: Input image in BGR format
            
        Returns:
            FaceDetectionResult containing landmarks
        """
        try:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process the image and detect face landmarks
            results = self.face_mesh.process(image_rgb)
            
            if not results.multi_face_landmarks:
                return FaceDetectionResult(success=True, face_count=0)
            
            # Extract landmarks
            landmarks = {}
            for face_landmarks in results.multi_face_landmarks:
                landmarks['face_oval'] = [
                    (landmark.x, landmark.y)
                    for landmark in face_landmarks.landmark[0:17]  # Face oval points
                ]
                landmarks['left_eyebrow'] = [
                    (landmark.x, landmark.y)
                    for landmark in face_landmarks.landmark[17:22]  # Left eyebrow
                ]
                landmarks['right_eyebrow'] = [
                    (landmark.x, landmark.y)
                    for landmark in face_landmarks.landmark[22:27]  # Right eyebrow
                ]
                landmarks['nose_bridge'] = [
                    (landmark.x, landmark.y)
                    for landmark in face_landmarks.landmark[27:31]  # Nose bridge
                ]
                landmarks['nose_tip'] = [
                    (landmark.x, landmark.y)
                    for landmark in face_landmarks.landmark[31:36]  # Nose tip
                ]
                landmarks['left_eye'] = [
                    (landmark.x, landmark.y)
                    for landmark in face_landmarks.landmark[36:42]  # Left eye
                ]
                landmarks['right_eye'] = [
                    (landmark.x, landmark.y)
                    for landmark in face_landmarks.landmark[42:48]  # Right eye
                ]
                landmarks['lips_outer'] = [
                    (landmark.x, landmark.y)
                    for landmark in face_landmarks.landmark[48:60]  # Outer lips
                ]
                landmarks['lips_inner'] = [
                    (landmark.x, landmark.y)
                    for landmark in face_landmarks.landmark[60:68]  # Inner lips
                ]
            
            return FaceDetectionResult(
                success=True,
                face_count=len(results.multi_face_landmarks),
                landmarks=landmarks
            )
            
        except Exception as e:
            logger.error(f"Error in face landmark detection: {e}")
            return FaceDetectionResult(
                success=False,
                error=str(e)
            )

class EngagementAnalyzer:
    """Analyze user engagement from video frames."""
    
    def __init__(self):
        """Initialize the engagement analyzer."""
        self.face_detector = FaceDetector()
        self.engagement_score = 0.5  # Neutral score
        self.decay_rate = 0.95  # Score decay rate per second
        self.last_update = 0
    
    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analyze a video frame for engagement.
        
        Args:
            frame: Input video frame in BGR format
            
        Returns:
            Dictionary containing engagement metrics
        """
        try:
            # Detect faces
            face_result = self.face_detector.detect_faces(frame)
            
            if not face_result.success or face_result.face_count == 0:
                return {
                    'success': False,
                    'error': 'No faces detected',
                    'engagement_score': 0.0
                }
            
            # Get face landmarks
            landmark_result = self.face_detector.detect_face_landmarks(frame)
            
            # Calculate engagement score (simplified example)
            engagement = self._calculate_engagement(face_result, landmark_result)
            
            # Update running score
            self.engagement_score = 0.7 * engagement + 0.3 * self.engagement_score
            
            return {
                'success': True,
                'engagement_score': float(self.engagement_score),
                'face_detected': True,
                'face_count': face_result.face_count,
                'landmarks_detected': landmark_result.success
            }
            
        except Exception as e:
            logger.error(f"Error in engagement analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'engagement_score': 0.0
            }
    
    def _calculate_engagement(self, face_result, landmark_result) -> float:
        """Calculate engagement score based on face and landmark data."""
        # Base score on face detection
        score = 0.5 if face_result.face_count > 0 else 0.0
        
        # Adjust based on landmarks if available
        if landmark_result.success and landmark_result.landmarks:
            # Add more sophisticated analysis here
            score += 0.2
        
        return min(max(score, 0.0), 1.0)
