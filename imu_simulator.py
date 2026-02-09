import numpy as np
from pyquaternion import Quaternion

class IMU_Simulator:
    """
    Simulates a 9-DOF IMU (MPU9250) and UWB (DW1000) for head tracking and positioning.
    Provides quaternion orientation and X, Y, Z coordinates.
    """
    def __init__(self, noise_level=0.01, drift_rate=0.001):
        self.noise_level = noise_level
        self.drift_rate = drift_rate
        
        # Orientation (Quaternion) - Initial state
        self.current_quat = Quaternion(1, 0, 0, 0)
        self.gyro_drift = np.zeros(3)
        
        # UWB Position (X, Y, Z) - Initial state
        self.current_pos = np.array([0.0, 0.0, 1.6])  # 1.6m height (approx ear level)
        self.pos_noise = 0.15  # ±15cm as per spec
        
    def get_raw_data(self, true_quat, true_pos):
        """
        Simulates raw sensor data by adding noise and drift to ground truth.
        """
        # Add drift to gyro
        self.gyro_drift += np.random.normal(0, self.drift_rate, 3)
        
        # Add noise to orientation
        noise_quat = Quaternion.random()
        fused_quat = Quaternion.slerp(true_quat, noise_quat, amount=self.noise_level)
        
        # Add noise to position
        noisy_pos = true_pos + np.random.normal(0, self.pos_noise, 3)
        
        return {
            "quat": fused_quat,
            "pos": noisy_pos,
            "accel": np.random.normal(0, 0.05, 3),  # Simulated accel
            "gyro": self.gyro_drift + np.random.normal(0, 0.01, 3)  # Simulated gyro
        }

    def update_demo_movement(self, time_step):
        """
        A demo mode to simulate head movement if no keyboard input is used.
        """
        # Simulate slight head bobbing and turning
        t = time_step
        yaw = 0.2 * np.sin(t * 0.5)
        pitch = 0.1 * np.cos(t * 0.3)
        
        # Update ground truth orientation
        target_quat = Quaternion(axis=[0, 0, 1], angle=yaw) * Quaternion(axis=[1, 0, 0], angle=pitch)
        
        # Update ground truth position (slight sway)
        target_pos = np.array([0.1 * np.sin(t * 0.2), 0.1 * np.cos(t * 0.2), 1.6])
        
        return self.get_raw_data(target_quat, target_pos)

if __name__ == "__main__":
    imu = IMU_Simulator()
    for i in range(5):
        data = imu.update_demo_movement(i * 0.1)
        print(f"Pos: {data['pos']}, Quat: {data['quat']}")
