import pyaudio
import numpy as np
from openwakeword.model import Model

class AtlasListener:
    def __init__(self):
        # Load the Alexa model
        self.model = Model(wakeword_models=["alexa"], inference_framework="onnx")
        self.CHUNK = 1280
        
        self.mic = pyaudio.PyAudio()
        self.stream = self.mic.open(
            format=pyaudio.paInt16, 
            channels=1, 
            rate=16000,
            input=True, 
            frames_per_buffer=self.CHUNK
        )

    def listen_for_wake_word(self):
        try:
            # Check if there is enough data in the mic buffer
            if self.stream.get_read_available() >= self.CHUNK:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                audio_buffer = np.frombuffer(data, dtype=np.int16)
                
                prediction = self.model.predict(audio_buffer)
                
                for mdl, score in prediction.items():
                    if score > 0.6: 
                        return mdl
            return None
        except Exception as e:
            # Only print on actual errors, not every loop
            return None


