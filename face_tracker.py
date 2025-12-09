"""
Face Tracker Module
Handles face detection and head pose estimation using MediaPipe
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Optional, Tuple


class FaceTracker:
    def __init__(self):
        """Initialize MediaPipe Face Mesh for face tracking"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        
        # Previous values for smoothing and jump detection
        self.prev_roll = None
        self.smoothing_factor = 0.3  # Lower = more smoothing
        
        # 3D model points for head pose estimation
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left Mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ])
        
    def get_head_pose(self, landmarks, image_shape) -> Dict[str, float]:
        """
        Calculate head pose angles (pitch, yaw, roll) from facial landmarks
        
        Args:
            landmarks: MediaPipe face landmarks
            image_shape: Shape of the input image (height, width, channels)
            
        Returns:
            Dictionary with pitch, yaw, and roll angles in degrees
        """
        height, width = image_shape[:2]
        
        # 2D image points from landmarks
        # Indices for key facial points in MediaPipe Face Mesh
        image_points = np.array([
            (landmarks[1].x * width, landmarks[1].y * height),      # Nose tip
            (landmarks[152].x * width, landmarks[152].y * height),  # Chin
            (landmarks[263].x * width, landmarks[263].y * height),  # Left eye left corner
            (landmarks[33].x * width, landmarks[33].y * height),    # Right eye right corner
            (landmarks[287].x * width, landmarks[287].y * height),  # Left mouth corner
            (landmarks[57].x * width, landmarks[57].y * height)     # Right mouth corner
        ], dtype="double")
        
        # Camera matrix (assuming standard webcam)
        focal_length = width
        center = (width / 2, height / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")
        
        # Assuming no lens distortion
        dist_coeffs = np.zeros((4, 1))
        
        # Solve PnP
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        # Convert rotation vector to rotation matrix
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        
        # Calculate Euler angles
        pose_matrix = cv2.hconcat((rotation_matrix, translation_vector))
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_matrix)
        
        pitch = euler_angles[0][0]
        yaw = euler_angles[1][0]
        roll = euler_angles[2][0]
        
        # Normalize roll to prevent 180-degree jumps
        # Keep roll within -90 to +90 degrees range
        if roll > 90:
            roll = roll - 180
        elif roll < -90:
            roll = roll + 180
        
        # Smooth roll values to prevent erratic jumps
        if self.prev_roll is not None:
            # Detect large jumps (more than 60 degrees)
            roll_diff = abs(roll - self.prev_roll)
            if roll_diff > 60:
                # If jump is too large, use previous value
                roll = self.prev_roll
            else:
                # Apply exponential smoothing
                roll = self.prev_roll + self.smoothing_factor * (roll - self.prev_roll)
        
        self.prev_roll = roll
        
        return {
            'pitch': float(pitch),  # Looking up/down
            'yaw': float(yaw),      # Looking left/right
            'roll': float(roll)     # Tilting head left/right
        }
    
    def process_frame(self, frame) -> Tuple[Optional[Dict[str, float]], np.ndarray]:
        """
        Process a video frame and extract head pose
        
        Args:
            frame: Input frame from camera
            
        Returns:
            Tuple of (head_pose_dict, annotated_frame)
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.face_mesh.process(rgb_frame)
        
        head_pose = None
        
        # Draw face mesh and calculate head pose
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw landmarks
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=self.drawing_spec,
                    connection_drawing_spec=self.drawing_spec
                )
                
                # Calculate head pose
                head_pose = self.get_head_pose(
                    face_landmarks.landmark,
                    frame.shape
                )
                
                # Draw pose information on frame
                if head_pose:
                    y_offset = 30
                    cv2.putText(frame, f"Pitch: {head_pose['pitch']:.1f}", 
                              (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Yaw: {head_pose['yaw']:.1f}", 
                              (10, y_offset + 30), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Roll: {head_pose['roll']:.1f}", 
                              (10, y_offset + 60), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.7, (0, 255, 0), 2)
        
        return head_pose, frame
    
    def release(self):
        """Release resources"""
        self.face_mesh.close()
