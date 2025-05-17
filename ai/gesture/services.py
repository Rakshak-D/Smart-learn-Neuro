import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

def process_gesture(video_frame):
    """
    Process a video frame to detect hand gestures using MediaPipe.
    Returns gesture type (e.g., 'swipe_left', 'swipe_right', 'none').
    """
    try:
        # Convert frame to RGB
        frame_rgb = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get x-coordinate of wrist (landmark 0)
                wrist_x = hand_landmarks.landmark[0].x
                # Simple heuristic: detect swipe based on wrist position
                if wrist_x < 0.3:
                    return "swipe_right"
                elif wrist_x > 0.7:
                    return "swipe_left"
        return "none"
    except Exception as e:
        print(f"Gesture processing error: {e}")
        return "none"