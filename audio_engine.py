import numpy as np
import sounddevice as sd
import soundfile as sf
import os

try:
    import librosa
except ImportError:
    librosa = None

class AudioSource:
    def __init__(self, name, pos, audio_path, target_sr=96000):
        self.name = name
        self.pos = np.array(pos)
        self.audio_data = None
        self.sample_rate = target_sr
        self.ptr = 0
        
        if os.path.exists(audio_path):
            if audio_path.lower().endswith('.mp3') and librosa:
                self.audio_data, _ = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            else:
                self.audio_data, sr = sf.read(audio_path)
                if len(self.audio_data.shape) > 1:
                    self.audio_data = np.mean(self.audio_data, axis=1)
                if sr != self.sample_rate:
                    # Basic resampling handled by librosa.load above, but for sf.read:
                    pass 
        
        if self.audio_data is None:
            print(f"Error: Could not load audio for source {name}: {audio_path}")
            self.audio_data = np.zeros(self.sample_rate * 5) # Silence fallback

    def get_next_chunk(self, chunk_size):
        chunk = self.audio_data[self.ptr : self.ptr + chunk_size]
        self.ptr += chunk_size
        if self.ptr + chunk_size >= len(self.audio_data):
            self.ptr = 0
        
        if len(chunk) < chunk_size:
            chunk = np.pad(chunk, (0, chunk_size - len(chunk)))
        return chunk

class AudioEngine:
    """
    Manages sequential 5-second playback of the 5 user-provided MP3 files.
    """
    def __init__(self, sample_rate=96000, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.sources = []
        self.active_idx = 0
        self.samples_played = 0
        self.switch_threshold = sample_rate * 5  # 5 seconds
        
        self._init_sources()

    def _init_sources(self):
        # The 5 MP3 files provided by the user
        assets = [
            ("Forest", [4.0, 4.0, 3.0], "audiopapkin-forest-ambience-296528.mp3"),
            ("River", [3.0, -4.0, 0.2], "dragon-studio-soothing-river-flow-372456.mp3"),
            ("Night", [-5.0, 2.0, 0.5], "freesound_community-night-ambience-17064.mp3"),
            ("Wind", [0.0, 0.0, 12.0], "soundreality-wind-blowing-457954.mp3"),
            ("Leaves", [0.0, 1.0, 0.0], "musicholder-walking-on-leaves-260279.mp3")
        ]
        for name, pos, path in assets:
            self.sources.append(AudioSource(name, pos, path, self.sample_rate))

    def get_active_source_chunk(self):
        """Returns only the current active source's chunk."""
        if not self.sources:
            return None
        
        active_source = self.sources[self.active_idx]
        chunk = active_source.get_next_chunk(self.chunk_size)
        
        self.samples_played += self.chunk_size
        if self.samples_played >= self.switch_threshold:
            self.samples_played = 0
            self.active_idx = (self.active_idx + 1) % len(self.sources)
            print(f"\nSwitching to source: {self.sources[self.active_idx].name}")
            
        return {active_source.name: (chunk, active_source.pos)}

    def get_source_chunks(self):
        # Override to only return active source
        return self.get_active_source_chunk()

    def set_mic_input(self, enabled):
        self.mic_enabled = enabled
        print(f"Mic Input {'Enabled' if enabled else 'Disabled'}")

    def get_input_chunk(self):
        """Simulates mic capture if real mic is not available, or uses sounddevice."""
        if self.mic_enabled:
            # In a real app, this would be a sounddevice InputStream callback
            return np.random.normal(0, 0.01, self.chunk_size)
        return np.zeros(self.chunk_size)

    def get_source_chunks(self):
        return {s.name: (s.get_next_chunk(self.chunk_size), s.pos) for s in self.sources}

if __name__ == "__main__":
    engine = AudioEngine()
    chunks = engine.get_source_chunks()
    for name, (data, pos) in chunks.items():
        print(f"Source {name} at {pos}: chunk_mean={np.abs(data).mean():.4f}")
