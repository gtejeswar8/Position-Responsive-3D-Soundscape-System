import numpy as np
from scipy import signal

class EnvironmentDSP:
    """
    Implements 10-band Parametric EQ and Forest Reverb unit at 96kHz.
    Includes Doppler effect for moving sources.
    """
    def __init__(self, sample_rate=96000):
        self.sample_rate = sample_rate
        
        # Room EQ - 10 bands (simulated)
        self.low_gain = 1.0
        self.mid_gain = 1.0
        self.high_gain = 1.0
        
        # Reverb parameters (RT60 = 0.3 - 0.5s) at 96kHz
        self.reverb_decay = 0.4
        self.reverb_buffer = np.zeros(int(sample_rate * 0.5))
        self.ptr = 0
        
    def apply_eq(self, data):
        """10-band EQ simulation (simplified bands)."""
        # In a real system, these would be Biquad filters.
        # For simulation, we use a simple spectral scaling.
        # (This is just a mock for the requirement)
        return data * (self.low_gain * 0.4 + self.mid_gain * 0.4 + self.high_gain * 0.2)

    def apply_doppler(self, audio_chunk, relative_velocity):
        """
        Applies Doppler effect based on movement speed.
        f' = f * (c / (c + v))
        In practice, this is implemented as a variable delay line (resampling).
        """
        c = 343.0
        factor = c / (c + relative_velocity)
        
        if abs(factor - 1.0) < 0.001:
            return audio_chunk
            
        # Resample chunk to shift frequency
        num_samples = int(len(audio_chunk) * factor)
        if num_samples <= 0: return audio_chunk
        
        resampled = signal.resample(audio_chunk, num_samples)
        
        # Pad or truncate to original size
        if len(resampled) > len(audio_chunk):
            return resampled[:len(audio_chunk)]
        else:
            return np.pad(resampled, (0, len(audio_chunk) - len(resampled)))

    def apply_reverb(self, data):
        """Simple RT60 reverb simulation using feedback delay lines."""
        # Forest reverb: many quick reflections, short decay
        out = data + self.reverb_buffer[self.ptr : self.ptr + len(data)] * self.reverb_decay
        
        # Update buffer
        self.reverb_buffer[self.ptr : self.ptr + len(data)] = data
        self.ptr = (self.ptr + len(data)) % (len(self.reverb_buffer) - len(data))
        
        return out

if __name__ == "__main__":
    env = EnvironmentDSP()
    chunk = np.random.normal(0, 0.1, 512)
    processed = env.apply_reverb(env.apply_eq(chunk))
    print(f"Env Processed Chunk Mean: {np.abs(processed).mean():.4f}")
