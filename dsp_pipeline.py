import numpy as np
from hrtf_engine import HRTF_Engine
from crosstalk import CrosstalkCanceller
from eq_reverb import EnvironmentDSP
from pyquaternion import Quaternion

class DSPPipeline:
    """
    Coordinates the signal flow at 96kHz:
    Source Chunks -> Doppler -> HRTF -> Mixer -> EQ -> Reverb -> CTC -> Output
    """
    def __init__(self, sample_rate=96000, chunk_size=1024):
        self.hrtf = HRTF_Engine(sample_rate, chunk_size*2)
        self.ctc = CrosstalkCanceller()
        self.env = EnvironmentDSP(sample_rate)
        self.chunk_size = chunk_size

    def process(self, sources_data, listener_pos, listener_quat):
        """
        sources_data: Dict mapping name to (audio_chunk, world_pos)
        listener_pos: [x, y, z]
        listener_quat: Quaternion orientation
        """
        mixed_l = np.zeros(self.chunk_size)
        mixed_r = np.zeros(self.chunk_size)
        
        inv_quat = listener_quat.inverse
        
        for name, (chunk, source_pos) in sources_data.items():
            # 1. Transform source position to listener-relative coordinate system
            rel_pos = source_pos - listener_pos
            # Rotate by inverse of head orientation to get relative azimuth/elevation
            local_pos = inv_quat.rotate(rel_pos)
            
            # 2. Compute Azimuth and Elevation
            dist = np.linalg.norm(local_pos)
            if dist < 0.1: dist = 0.1
            
            azimuth = np.degrees(np.arctan2(local_pos[0], local_pos[1]))
            elevation = np.degrees(np.arcsin(local_pos[2] / dist))
            
            # 3. Distance attenuation (Inverse square law approximation)
            attenuation = 1.0 / (dist + 1.0)
            chunk = chunk * attenuation
            
            # 4. Apply Doppler (Simulated based on radial velocity)
            # For simplicity, we assume static sources for now, but hook is here
            processed_chunk = self.env.apply_doppler(chunk, 0.0)
            
            # 5. Apply HRTF
            l, r = self.hrtf.spatialize_source(processed_chunk, azimuth, elevation)
            
            mixed_l += l
            mixed_r += r
            
        # 6. Post-mix DSP (EQ & Reverb)
        mixed_l = self.env.apply_reverb(self.env.apply_eq(mixed_l))
        mixed_r = self.env.apply_reverb(self.env.apply_eq(mixed_r))
        
        # 7. Crosstalk Cancellation (CTC)
        final_l, final_r = self.ctc.process(mixed_l, mixed_r)
        
        return final_l, final_r

if __name__ == "__main__":
    pipeline = DSPPipeline()
    sources = {"Bird": (np.random.normal(0, 0.1, 512), np.array([1, 1, 1]))}
    l, r = pipeline.process(sources, np.array([0,0,1.6]), Quaternion(1,0,0,0))
    print(f"Pipeline output L_mean={np.abs(l).mean():.4f}, R_mean={np.abs(r).mean():.4f}")
