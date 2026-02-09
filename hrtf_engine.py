import numpy as np
from scipy import signal
from scipy.fft import fft, ifft

class HRTF_Engine:
    """
    Handles HRTF lookup and FFT-based convolution at 96kHz.
    Simulates a 288-direction resolution (24 azimuth x 12 elevation).
    """
    def __init__(self, sample_rate=96000, fft_size=2048):
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.num_azimuth = 24
        self.num_elevation = 12
        
        # Simulate HRTF Database (Hihger resolution for 96kHz)
        self.filter_length = 1024  # More taps for 96kHz precision
        self.hrtf_db = self._generate_synthetic_hrtf()
        
    def _generate_synthetic_hrtf(self):
        """Generates synthetic HRTF filters with refined ITD/ILD for 96kHz."""
        db = {}
        for el in range(self.num_elevation):
            elevation = el * 15 - 90
            db[elevation] = {}
            for az in range(self.num_azimuth):
                azimuth = az * 15
                
                # Precise ITD for 96kHz (max approx 0.8ms -> 77 samples)
                # Woodworth's model: ITD = (r/c) * (theta + sin(theta))
                r = 0.0875 # Head radius in meters
                c = 343.0
                theta = np.radians(azimuth % 180) # Angle from midline
                itd_sec = (r/c) * (theta + np.sin(theta))
                if azimuth > 180: itd_sec = -itd_sec
                
                itd_samples = int(round(itd_sec * self.sample_rate))
                
                # Refined ILD: approx ±20dB based on frequency and angle
                # Simple model: Gain = 1 - 0.5 * sin(theta) for contralateral ear
                ild_factor = 0.5 + 0.5 * np.cos(np.radians(azimuth))
                
                ir_l = np.zeros(self.filter_length)
                ir_r = np.zeros(self.filter_length)
                
                # Offset to allow for causal ITD
                base_idx = 100
                idx_l = base_idx + (itd_samples // 2 if itd_samples > 0 else 0)
                idx_r = base_idx + (-itd_samples // 2 if itd_samples < 0 else 0)
                
                ir_l[idx_l] = 1.0 * (1.0 if itd_samples >= 0 else ild_factor)
                ir_r[idx_r] = 1.0 * (1.0 if itd_samples <= 0 else ild_factor)
                
                # Add complex HF acoustic features (pinna notches etc)
                t = np.arange(self.filter_length)
                ir_l += 0.05 * np.exp(-t/100) * np.sin(2 * np.pi * 7000 * t / self.sample_rate)
                ir_r += 0.05 * np.exp(-t/100) * np.sin(2 * np.pi * 7000 * t / self.sample_rate)
                
                db[elevation][azimuth] = (fft(ir_l, self.fft_size), fft(ir_r, self.fft_size))
        return db

    def get_nearest_hrtf(self, azimuth, elevation):
        """Looks up the closest HRTF coefficients."""
        # Normalize azimuth 0-360
        azimuth = azimuth % 360
        # Snap to 15 degree grid
        az_idx = int(round(azimuth / 15.0)) % 24
        el_idx = int(round((elevation + 90) / 15.0))
        el_idx = max(0, min(11, el_idx))
        
        target_az = az_idx * 15
        target_el = el_idx * 15 - 90
        
        return self.hrtf_db[target_el][target_az]

    def spatialize_source(self, audio_chunk, azimuth, elevation):
        """
        Applies HRTF to a single mono source using Overlap-Save convolution.
        """
        ir_fft_l, ir_fft_r = self.get_nearest_hrtf(azimuth, elevation)
        
        source_fft = fft(audio_chunk, self.fft_size)
        
        out_l = np.real(ifft(source_fft * ir_fft_l))[:len(audio_chunk)]
        out_r = np.real(ifft(source_fft * ir_fft_r))[:len(audio_chunk)]
        
        return out_l, out_r

if __name__ == "__main__":
    engine = HRTF_Engine()
    dummy_source = np.random.normal(0, 0.1, 512)
    l, r = engine.spatialize_source(dummy_source, 45, 0)
    print(f"Spatialized Chunk: L_mean={np.abs(l).mean():.4f}, R_mean={np.abs(r).mean():.4f}")
