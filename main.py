import numpy as np
import sounddevice as sd
import time
import sys
import threading
from stm32_controller_sim import STM32_Controller
from imu_simulator import IMU_Simulator
from sensor_fusion import SensorFusion
from audio_engine import AudioEngine
from dsp_pipeline import DSPPipeline
from pyquaternion import Quaternion

# Optional dependency for keyboard control
try:
    import keyboard
except ImportError:
    keyboard = None

class MudumalaiSystem:
    def __init__(self):
        self.sample_rate = 96000
        self.chunk_size = 1024
        
        # Initialize modules
        self.controller = STM32_Controller(self.sample_rate, self.chunk_size)
        self.imu = IMU_Simulator()
        self.fusion = SensorFusion()
        self.audio = AudioEngine(self.sample_rate, self.chunk_size)
        self.pipeline = DSPPipeline(self.sample_rate, self.chunk_size)
        
        # State
        self.current_pos = np.array([0.0, 0.0, 1.6])
        self.current_quat = Quaternion(1, 0, 0, 0)
        self.base_pos = np.array([0.0, 0.0, 1.6])
        self.base_yaw = 0.0
        self.base_pitch = 0.0
        self.start_time = time.time()
        self.demo_mode = True
        
        # Audio Stream
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=self.chunk_size,
            channels=2,
            callback=self._audio_callback
        )

    def _timer_interrupt_100hz(self):
        """STM32 Timer Interrupt (100Hz) - Sensor Fusion and Update Positioning."""
        # 1. Check Keyboard Inputs (Manual Control)
        if keyboard:
            if keyboard.is_pressed('w'): self.base_pos[1] += 0.05
            if keyboard.is_pressed('s'): self.base_pos[1] -= 0.05
            if keyboard.is_pressed('a'): self.base_pos[0] -= 0.05
            if keyboard.is_pressed('d'): self.base_pos[0] += 0.05
            if keyboard.is_pressed('left'): self.base_yaw += 3.0
            if keyboard.is_pressed('right'): self.base_yaw -= 3.0
            if keyboard.is_pressed('up'): self.base_pitch += 2.0
            if keyboard.is_pressed('down'): self.base_pitch -= 2.0
            
            # Disable demo if user interacts
            if any(keyboard.is_pressed(k) for k in ['w','s','a','d','left','right','up','down']):
                self.demo_mode = False

        # 2. Get Raw Data (Demo or Manual)
        if self.demo_mode:
            elapsed = time.time() - self.start_time
            raw_data = self.imu.update_demo_movement(elapsed)
        else:
            target_quat = Quaternion(axis=[0, 0, 1], angle=np.radians(self.base_yaw)) * \
                          Quaternion(axis=[1, 0, 0], angle=np.radians(self.base_pitch))
            raw_data = self.imu.get_raw_data(target_quat, self.base_pos)
        
        # 3. Execute Kalman filtering
        fused = self.fusion.update(raw_data)
        self.current_pos = fused['pos']
        self.current_quat = fused['quat']

    def _audio_callback(self, outdata, frames, time_info, status):
        """Audio DMA Callback."""
        if status:
            print(f"Audio Error: {status}")
            
        # 1. Get audio chunks from all 6 sources
        sources_data = self.audio.get_source_chunks()
        
        # 2. Process through DSP Pipeline
        final_l, final_r = self.pipeline.process(
            sources_data, 
            self.current_pos, 
            self.current_quat
        )
        
        # 3. Interleave and write to output
        outdata[:, 0] = final_l
        outdata[:, 1] = final_r

    def start(self):
        print("\n" + "="*40)
        print("MUDUMALAI 3D SOUNDSCAPE SYSTEM STARTING")
        print("="*40)
        print("Simulating STM32H7 Environment...")
        print("DSP: HRTF Spatializer (288 directions)")
        print("Sensors: UWB + 9-DOF IMU (Fused @ 100Hz)")
        print("Sources: Sequential 5-second MP3 Multiplexing (5 assets)")
        print("="*40)
        print("CONTROLS:")
        print("  WASD : Move position (X, Y)")
        print("  ARROWS : Look around (Yaw, Pitch)")
        print("  Current Mode: " + ("DEMO (Auto-movement)" if self.demo_mode else "MANUAL"))
        print("="*40)
        
        self.controller.start(self._timer_interrupt_100hz, None)
        self.stream.start()
        
        print("\nSYSTEM RUNNING.")
        print("Press Ctrl+C to Stop.")
        
        try:
            while True:
                if not self.demo_mode:
                    sys.stdout.write(f"\rPos: [{self.current_pos[0]:.2f}, {self.current_pos[1]:.2f}, {self.current_pos[2]:.2f}] | Yaw: {self.base_yaw:.1f}°   ")
                    sys.stdout.flush()
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        print("\nShutting down Mudumalai System...")
        self.stream.stop()
        self.controller.stop()
        print("System Stopped.")

def start():
    system = MudumalaiSystem()
    system.start()

if __name__ == "__main__":
    start()
