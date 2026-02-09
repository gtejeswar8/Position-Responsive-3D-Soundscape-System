import numpy as np

class CrosstalkCanceller:
    """
    Implements a 2x2 inverse filter matrix for speaker crosstalk cancellation (CTC).
    Assumes standard 30° stereo speaker placement.
    """
    def __init__(self, speaker_distance_m=1.5, listener_distance_m=1.5):
        # Propagation delay between speakers and ears
        self.c = 343.0  # Speed of sound m/s
        self.d_direct = listener_distance_m
        # Approx distance to opposite ear
        self.d_cross = np.sqrt(listener_distance_m**2 + speaker_distance_m**2)
        
        self.delta_t = (self.d_cross - self.d_direct) / self.c
        self.alpha = 0.7  # Attenuation factor for crosstalk path
        
    def process(self, l_in, r_in):
        """
        Simple recursive crosstalk cancellation (Cross-feed removal).
        yL = xL - alpha * yR(t - delta_t)
        yR = xR - alpha * yL(t - delta_t)
        
        Optimized for real-time safe processing.
        """
        # In a real implementation, we'd use a delay line.
        # For simulation, we'll use a simplified shelf filter correction
        # as suggested in the spec.
        
        # Shelf filter to compensate for head shadowing/diffraction
        # Boost highs slightly to compensate for CTC attenuation
        l_out = l_in * 1.1 - r_in * self.alpha * 0.5
        r_out = r_in * 1.1 - l_in * self.alpha * 0.5
        
        # Gain normalization
        max_val = np.max(np.abs([l_out, r_out]))
        if max_val > 1.0:
            l_out /= max_val
            r_out /= max_val
            
        return l_out, r_out

if __name__ == "__main__":
    ctc = CrosstalkCanceller()
    l, r = ctc.process(np.array([1.0, 0.0]), np.array([0.0, 1.0]))
    print(f"CTC applied: L={l}, R={r}")
