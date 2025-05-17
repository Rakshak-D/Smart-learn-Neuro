import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
import json

class FaceDetector:
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def detect_gestures(self, frame):
        """Detect facial gestures from video frame"""
        # Convert frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        results = self.face_mesh.process(frame_rgb)
        
        if results.multi_face_landmarks:
            # Get facial landmarks
            landmarks = results.multi_face_landmarks[0].landmark
            
            # Detect gestures
            gestures = self._analyze_gestures(landmarks)
            
            return gestures
        
        return None
    
    def _analyze_gestures(self, landmarks):
        """Analyze facial landmarks for gestures"""
        gestures = {}
        
        # Get key points
        left_eye = landmarks[33]  # Left eye
        right_eye = landmarks[133]  # Right eye
        mouth = landmarks[13]  # Mouth center
        
        # Detect confusion (frequent blinking)
        if self._detect_blink(landmarks):
            gestures['confused'] = True
        
        # Detect stuck (frequent mouth movements)
        if self._detect_mouth_movement(landmarks):
            gestures['stuck'] = True
        
        # Detect boredom (looking away)
        if self._detect_look_away(landmarks):
            gestures['bored'] = True
        
        # Detect focus (steady gaze)
        if self._detect_focus(landmarks):
            gestures['focused'] = True
        
        return gestures
    
    def _detect_blink(self, landmarks):
        """Detect blinking"""
        # Get eye landmarks
        left_eye = [landmarks[i] for i in range(33, 133)]
        right_eye = [landmarks[i] for i in range(133, 233)]
        
        # Calculate eye aspect ratio
        left_ratio = self._eye_aspect_ratio(left_eye)
        right_ratio = self._eye_aspect_ratio(right_eye)
        
        # Check if both eyes are closed
        if left_ratio < 0.2 and right_ratio < 0.2:
            return True
        return False
    
    def _eye_aspect_ratio(self, eye):
        """Calculate eye aspect ratio"""
        # Get vertical distances
        v1 = self._distance(eye[1], eye[5])
        v2 = self._distance(eye[2], eye[4])
        
        # Get horizontal distance
        h = self._distance(eye[0], eye[3])
        
        return (v1 + v2) / (2.0 * h)
    
    def _distance(self, p1, p2):
        """Calculate distance between two points"""
        return np.sqrt(
            (p1.x - p2.x) ** 2 +
            (p1.y - p2.y) ** 2
        )
    
    def _detect_mouth_movement(self, landmarks):
        """Detect mouth movement"""
        # Get mouth landmarks
        top_lip = landmarks[0]
        bottom_lip = landmarks[17]
        
        # Calculate mouth opening
        mouth_open = self._distance(top_lip, bottom_lip)
        
        # Check if mouth is open
        if mouth_open > 0.05:
            return True
        return False
    
    def _detect_look_away(self, landmarks):
        """Detect if user is looking away"""
        # Get nose tip and eye landmarks
        nose_tip = landmarks[4]
        left_eye = landmarks[33]
        right_eye = landmarks[133]
        
        # Calculate gaze direction
        gaze_vector = np.array([
            (left_eye.x + right_eye.x) / 2 - nose_tip.x,
            (left_eye.y + right_eye.y) / 2 - nose_tip.y
        ])
        
        # Check if looking away
        if np.linalg.norm(gaze_vector) > 0.1:
            return True
        return False
    
    def _detect_focus(self, landmarks):
        """Detect if user is focused"""
        # Get eye landmarks
        left_eye = landmarks[33]
        right_eye = landmarks[133]
        
        # Calculate eye movement
        eye_movement = self._distance(left_eye, right_eye)
        
        # Check if eyes are steady
        if eye_movement < 0.01:
            return True
        return False
