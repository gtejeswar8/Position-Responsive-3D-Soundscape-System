import time
import threading
import numpy as np

class STM32_Controller:
    """
    Simulates an STM32H7 (Cortex-M7) controller behavior at 96kHz.
    Includes a 100Hz timer interrupt and dual-buffer DMA-style callbacks.
    """
    def __init__(self, sample_rate=96000, buffer_size=1024):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.running = False
        self.timer_thread = None
        self.audio_dma_callback = None
        self.timer_callback = None
        
        # Performance monitoring
        self.last_timer_time = 0
        self.timer_jitter = 0
        
        # DMA State: Double-buffering simulation
        self.dma_buffer_idx = 0  # 0 or 1 for half-buffer completion
        self.processed_buffers = 0

    def start(self, timer_cb, audio_cb):
        """
        Starts the simulation with specified callbacks.
        timer_cb: Function to call at 100Hz.
        audio_cb: Function to call for audio buffer processing.
        """
        self.timer_callback = timer_cb
        self.audio_dma_callback = audio_cb
        self.running = True
        
        # Start timer thread (100Hz = 10ms period)
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
        
        print(f"STM32 Simulation Started ({self.sample_rate}Hz, 100Hz Timer, Dual-DMA)")

    def stop(self):
        self.running = False
        if self.timer_thread:
            # Note: joining daemon thread might not be necessary but good for cleanup
            pass
        print("STM32 Simulation Stopped")

    def _timer_loop(self):
        """100Hz hardware timer interrupt simulation."""
        target_period = 0.01  # 10ms
        self.last_timer_time = time.perf_counter()
        
        while self.running:
            current_time = time.perf_counter()
            elapsed = current_time - self.last_timer_time
            
            if elapsed >= target_period:
                self.timer_jitter = elapsed - target_period
                self.last_timer_time = current_time
                
                if self.timer_callback:
                    # Execute control logic (e.g., sensor fusion update)
                    self.timer_callback()
            
            # Yield to CPU
            time.sleep(0.001)

    def process_audio_dma(self, in_data):
        """
        Simulates DMA-triggered audio processing with double buffering.
        Half-buffer complete interrupt simulation.
        """
        self.dma_buffer_idx = (self.dma_buffer_idx + 1) % 2
        self.processed_buffers += 1
        
        if self.audio_dma_callback:
            return self.audio_dma_callback(in_data)
        return in_data

if __name__ == "__main__":
    # Test stub
    def mock_timer():
        print(f"Timer IRQ at {time.time():.4f}")

    def mock_audio(data):
        return data * 0.5  # Simple gain reduction

    controller = STM32_Controller()
    controller.start(mock_timer, mock_audio)
    
    try:
        time.sleep(0.1)  # Run for a bit
    finally:
        controller.stop()
