import numpy as np
from pyquaternion import Quaternion

class KalmanFilter3D:
    """
    Simple Linear Kalman Filter for smoothing UWB position and IMU orientation.
    In a real system, an Extended Kalman Filter (EKF) would be used for Quaternions.
    """
    def __init__(self, dt=0.01):
        self.dt = dt
        
        # State: [x, y, z, vx, vy, vz]
        self.pos_state = np.zeros(6)
        self.pos_P = np.eye(6) * 1.0  # Covariance
        
        # Process Noise
        self.pos_Q = np.eye(6) * 0.01
        
        # Measurement Noise (UWB ±15cm)
        self.pos_R = np.eye(3) * 0.15
        
        # Transition Matrix
        self.pos_F = np.eye(6)
        self.pos_F[0, 3] = dt
        self.pos_F[1, 4] = dt
        self.pos_F[2, 5] = dt
        
        # Measurement Matrix (We only measure x, y, z)
        self.pos_H = np.zeros((3, 6))
        self.pos_H[0, 0] = 1
        self.pos_H[1, 1] = 1
        self.pos_H[2, 2] = 1

    def predict(self):
        # Position Prediction
        self.pos_state = self.pos_F @ self.pos_state
        self.pos_P = self.pos_F @ self.pos_P @ self.pos_F.T + self.pos_Q

    def update_position(self, z):
        # Measurement Update
        y = z - self.pos_H @ self.pos_state  # Innovation
        S = self.pos_H @ self.pos_P @ self.pos_H.T + self.pos_R
        K = self.pos_P @ self.pos_H.T @ np.linalg.inv(S)  # Kalman Gain
        
        self.pos_state = self.pos_state + K @ y
        self.pos_P = (np.eye(6) - K @ self.pos_H) @ self.pos_P

    def filter_orientation(self, quat_measure, last_quat, alpha=0.9):
        """
        Simple complementary filter for orientation instead of EKF for simplicity.
        In a firmware context, this saves cycles while remaining effective.
        """
        return Quaternion.slerp(last_quat, quat_measure, amount=(1.0 - alpha))

class SensorFusion:
    def __init__(self):
        self.kf = KalmanFilter3D()
        self.current_pos = np.array([0.0, 0.0, 1.6])
        self.current_quat = Quaternion(1, 0, 0, 0)

    def update(self, raw_data):
        # Position Update
        self.kf.predict()
        self.kf.update_position(raw_data['pos'])
        self.current_pos = self.kf.pos_state[:3]
        
        # Orientation Update
        self.current_quat = self.kf.filter_orientation(raw_data['quat'], self.current_quat)
        
        return {
            "pos": self.current_pos,
            "quat": self.current_quat
        }

if __name__ == "__main__":
    fusion = SensorFusion()
    raw = {"pos": np.array([0.1, 0.1, 1.65]), "quat": Quaternion(1, 0, 0.1, 0)}
    fused = fusion.update(raw)
    print(f"Fused Pos: {fused['pos']}, Fused Quat: {fused['quat']}")
