import cv2
import numpy as np
import mediapipe as mp
import os
import logging

class MalpracticeDetector:
    def __init__(self):
        """Initialize detection models"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize MediaPipe models
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Initialize simple object detection (placeholder for YOLO)
        # For demonstration purposes, we'll use simple color-based detection
        self.yolo_model = None  # Simplified version without YOLO
        
        # Talking detection parameters
        self.prev_mouth_landmarks = None
        self.mouth_movement_threshold = 0.01
        
        # Detection cooldown to prevent spam
        self.last_detection_time = {}
        self.detection_cooldown = 2.0  # seconds
    
    def detect_hand_gestures(self, frame):
        """Detect suspicious hand gestures"""
        detections = []
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Analyze hand gesture for suspicious behavior
                if self._is_suspicious_hand_gesture(hand_landmarks):
                    # Get bounding box for hand
                    h, w, _ = frame.shape
                    x_coords = [landmark.x * w for landmark in hand_landmarks.landmark]
                    y_coords = [landmark.y * h for landmark in hand_landmarks.landmark]
                    
                    x_min, x_max = int(min(x_coords)), int(max(x_coords))
                    y_min, y_max = int(min(y_coords)), int(max(y_coords))
                    
                    # Add padding
                    padding = 20
                    x_min = max(0, x_min - padding)
                    y_min = max(0, y_min - padding)
                    x_max = min(w, x_max + padding)
                    y_max = min(h, y_max + padding)
                    
                    # Draw bounding box
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
                    cv2.putText(frame, 'SUSPICIOUS GESTURE', (x_min, y_min - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    detections.append({
                        'type': 'hand_gestures',
                        'confidence': 0.85,
                        'bbox': (x_min, y_min, x_max, y_max)
                    })
        
        return detections
    
    def detect_mobile_phone(self, frame):
        """Detect mobile phones using simple color/edge detection (placeholder for YOLO)"""
        detections = []
        
        try:
            # Simple edge-based detection as a placeholder
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Filter by area and aspect ratio to detect rectangular objects
                area = cv2.contourArea(contour)
                if 1000 < area < 8000:  # Approximate mobile phone size
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(w) / h
                    
                    # Mobile phones typically have aspect ratio between 0.4 and 0.8
                    if 0.4 < aspect_ratio < 0.8:
                        # Simulate detection confidence
                        confidence = 0.75
                        
                        # Draw bounding box
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                        cv2.putText(frame, f'MOBILE PHONE ({confidence:.2f})', 
                                  (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                        
                        detections.append({
                            'type': 'mobile_phone',
                            'confidence': confidence,
                            'bbox': (x, y, x + w, y + h)
                        })
                        
                        # Limit to one detection per frame to avoid spam
                        break
        
        except Exception as e:
            self.logger.error(f"Error in mobile phone detection: {e}")
        
        return detections
    
    def detect_talking(self, frame):
        """Detect talking/mouth movements"""
        detections = []
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Get mouth landmarks (lips)
                mouth_landmarks = self._get_mouth_landmarks(face_landmarks)
                
                if self.prev_mouth_landmarks is not None:
                    # Calculate mouth movement
                    movement = self._calculate_mouth_movement(mouth_landmarks, self.prev_mouth_landmarks)
                    
                    if movement > self.mouth_movement_threshold:
                        # Draw face mesh (mouth area)
                        h, w, _ = frame.shape
                        mouth_points = [(int(landmark.x * w), int(landmark.y * h)) 
                                      for landmark in mouth_landmarks]
                        
                        if mouth_points:
                            # Get bounding box for mouth area
                            x_coords = [p[0] for p in mouth_points]
                            y_coords = [p[1] for p in mouth_points]
                            x_min, x_max = min(x_coords), max(x_coords)
                            y_min, y_max = min(y_coords), max(y_coords)
                            
                            # Add padding
                            padding = 30
                            x_min = max(0, x_min - padding)
                            y_min = max(0, y_min - padding)
                            x_max = min(w, x_max + padding)
                            y_max = min(h, y_max + padding)
                            
                            # Draw bounding box
                            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 255), 2)
                            cv2.putText(frame, 'TALKING DETECTED', (x_min, y_min - 10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                            
                            detections.append({
                                'type': 'talking',
                                'confidence': min(movement * 10, 1.0),  # Normalize movement to confidence
                                'bbox': (x_min, y_min, x_max, y_max)
                            })
                
                self.prev_mouth_landmarks = mouth_landmarks
        
        return detections
    
    def _is_suspicious_hand_gesture(self, hand_landmarks):
        """Analyze hand landmarks to detect suspicious gestures"""
        # Get key landmarks
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]
        wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        
        # Calculate distances
        thumb_index_distance = np.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
        
        # Detect writing gesture (thumb and index finger close together)
        if thumb_index_distance < 0.05:
            return True
        
        # Detect pointing gesture (index finger extended, others closed)
        index_wrist_distance = np.sqrt((index_tip.x - wrist.x)**2 + (index_tip.y - wrist.y)**2)
        middle_wrist_distance = np.sqrt((middle_tip.x - wrist.x)**2 + (middle_tip.y - wrist.y)**2)
        
        if index_wrist_distance > 0.2 and middle_wrist_distance < 0.15:
            return True
        
        return False
    
    def _get_mouth_landmarks(self, face_landmarks):
        """Extract mouth landmarks from face mesh"""
        # Mouth landmark indices in MediaPipe face mesh
        mouth_indices = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
        return [face_landmarks.landmark[i] for i in mouth_indices]
    
    def _calculate_mouth_movement(self, current_landmarks, prev_landmarks):
        """Calculate movement between current and previous mouth landmarks"""
        if len(current_landmarks) != len(prev_landmarks):
            return 0
        
        total_movement = 0
        for curr, prev in zip(current_landmarks, prev_landmarks):
            movement = np.sqrt((curr.x - prev.x)**2 + (curr.y - prev.y)**2)
            total_movement += movement
        
        return total_movement / len(current_landmarks)
    
    def _should_detect(self, detection_type):
        """Check if enough time has passed since last detection of this type"""
        import time
        current_time = time.time()
        last_time = self.last_detection_time.get(detection_type, 0)
        
        if current_time - last_time >= self.detection_cooldown:
            self.last_detection_time[detection_type] = current_time
            return True
        return False
    
    def process_frame(self, frame):
        """Process a single frame and return annotated frame with detections"""
        detections = []
        
        # Make a copy of the frame for processing
        processed_frame = frame.copy()
        
        # Detect hand gestures
        hand_detections = self.detect_hand_gestures(processed_frame)
        if hand_detections and self._should_detect('hand_gestures'):
            detections.extend(hand_detections)
        
        # Detect mobile phones
        mobile_detections = self.detect_mobile_phone(processed_frame)
        if mobile_detections and self._should_detect('mobile_phone'):
            detections.extend(mobile_detections)
        
        # Detect talking
        talking_detections = self.detect_talking(processed_frame)
        if talking_detections and self._should_detect('talking'):
            detections.extend(talking_detections)
        
        # Add timestamp overlay
        timestamp = cv2.getTickCount()
        cv2.putText(processed_frame, f'Frame: {timestamp}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return processed_frame, detections
