"""import subprocess
import os
import time
import pygame

class AtlasSpeaker:
    def __init__(self):
        # Anchor paths to the project root
        self.root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.piper_exe = os.path.join(self.root, "assets", "piper_windows_amd64","piper", "piper.exe")
        self.model = os.path.join(self.root, "assets",  "piper_windows_amd64","piper", "en_US-amy-medium.onnx")
        self.temp_wav = os.path.join(self.root, "assets", "piper_windows_amd64","piper", "temp_speech.wav")
        
        os.makedirs(os.path.dirname(self.temp_wav), exist_ok=True)
        pygame.mixer.init()

    def speak(self, text):
        if not text: return
        try:
            # 1. Generate Speech
            process = subprocess.Popen(
                [self.piper_exe, "--model", self.model, "--output_file", self.temp_wav],
                stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            process.communicate(input=text.encode('utf-8'))
            process.wait()

            # 2. Play and BLOCK (Wait for finish)
            if os.path.exists(self.temp_wav):
                pygame.mixer.music.load(self.temp_wav)
                pygame.mixer.music.play()
                
                # The 'While' loop stops the script until audio is done
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.music.unload()
        except Exception as e:
            print(f"Speaker Error: {e}")"""
            

# import subprocess
# import os
# import time
# import pygame

# class AtlasSpeaker:
#     def __init__(self):
#         self.root = r"C:\Users\madhu\OneDrive\Desktop\Atlas"
#         self.piper_exe = os.path.join(self.root, "assets", "piper_windows_amd64","piper", "piper.exe")
#         self.model = os.path.join(self.root, "assets", "piper_windows_amd64","piper","en_US-lessac-medium.onnx")
#         self.temp_wav = os.path.join(self.root, "assets", "piper_windows_amd64","piper", "temp_speech.wav")
        
#         os.makedirs(os.path.dirname(self.temp_wav), exist_ok=True)
#         # Force pygame to use a specific frequency for better compatibility
#         pygame.mixer.quit() 
#         pygame.mixer.init(frequency=22050, size=-16, channels=1)

#     def speak(self, text):
#         if not text: return
#         try:
#             # Clean up old audio file to prevent 'file locked' errors
#             if os.path.exists(self.temp_wav):
#                 try: os.remove(self.temp_wav)
#                 except: pass

#             # Generate audio
#             process = subprocess.Popen(
#                 [self.piper_exe, "--model", self.model, "--output_file", self.temp_wav],
#                 stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
#             )
#             process.communicate(input=text.encode('utf-8'))
#             process.wait()

#             if os.path.exists(self.temp_wav):
#                 pygame.mixer.music.load(self.temp_wav)
#                 pygame.mixer.music.play()
#                 # BLOCKING LOOP: This is what stops the flicker!
#                 while pygame.mixer.music.get_busy():
#                     time.sleep(0.1)
#                 pygame.mixer.music.unload()
#         except Exception as e:
#             print(f"Speaker Error: {e}")
import subprocess
import os
import time
import threading
import pygame
import numpy as np
import wave
import speech_recognition as sr


class AtlasInterrupted(Exception):
    """Raised when the user says a stop-word while Atlas is speaking."""
    pass


_STOP_PHRASES = frozenset({"stop", "wait", "hold on", "pause", "be quiet", "quiet"})


class AtlasSpeaker:
    def __init__(self):
        self.root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.piper_exe = os.path.join(self.root, "assets", "piper_windows_amd64","piper", "piper.exe")
        self.model = os.path.join(self.root, "assets", "piper_windows_amd64","piper","en_US-lessac-medium.onnx")
        self.temp_wav = os.path.join(self.root, "assets", "piper_windows_amd64","piper", "temp_speech.wav")

        os.makedirs(os.path.dirname(self.temp_wav), exist_ok=True)
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050)

        self._stop_event = threading.Event()
        self._interrupt_text = None
        self._was_interrupted = False
        self.resume_text = None
        self.is_speaking = False

    def stop_speaking(self):
        self._stop_event.set()
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.is_speaking = False

    def _run_interrupt_listener(self, stop_event):
        """Polls the microphone while TTS plays; stops only on stop-words."""
        recorder = sr.Recognizer()
        recorder.energy_threshold = 500
        recorder.dynamic_energy_threshold = False

        # Short delay so we don't accidentally capture the start of our own TTS
        time.sleep(0.6)

        while not stop_event.is_set():
            try:
                with sr.Microphone() as source:
                    audio = recorder.listen(source, timeout=1.0, phrase_time_limit=4)
                    text = recorder.recognize_google(audio)
                    if text and not stop_event.is_set():
                        low = text.lower().strip()
                        if any(phrase in low for phrase in _STOP_PHRASES):
                            self._interrupt_text = text
                            self._was_interrupted = True
                            stop_event.set()
                            pygame.mixer.music.stop()
                            return
            except sr.WaitTimeoutError:
                pass
            except Exception:
                pass

    def speak(self, text, signals=None, interruptible=True):
        """
        Speak text via Piper TTS with real-time lip-sync animation.
        Raises AtlasInterrupted (storing resume_text) if the user says a stop-word.
        Pass interruptible=False for short acknowledgment phrases that should never be stopped.
        """
        if not text:
            return None

        self._stop_event.clear()
        self._interrupt_text = None
        self._was_interrupted = False
        self.is_speaking = True

        try:
            process = subprocess.Popen(
                [self.piper_exe, "--model", self.model, "--output_file", self.temp_wav, "--length_scale", "0.95"],
                stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            process.communicate(input=text.encode('utf-8'))
            process.wait()

            if not os.path.exists(self.temp_wav):
                return None

            with wave.open(self.temp_wav, 'rb') as wf:
                params = wf.getparams()
                frames = wf.readframes(params.nframes)
                audio_data = np.frombuffer(frames, dtype=np.int16).astype(float)

            if len(audio_data) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data))

            if interruptible:
                threading.Thread(
                    target=self._run_interrupt_listener,
                    args=(self._stop_event,),
                    daemon=True
                ).start()

            pygame.mixer.music.load(self.temp_wav)
            pygame.mixer.music.play()

            sample_rate = params.framerate
            start_time = time.time()

            while pygame.mixer.music.get_busy() and not self._stop_event.is_set():
                elapsed = time.time() - start_time
                current_sample = int(elapsed * sample_rate)
                window = audio_data[current_sample: current_sample + 1024]

                if len(window) > 0 and signals:
                    volume = np.max(np.abs(window))
                    if volume > 0.8:
                        signals.update_avatar.emit("gesture")
                    elif volume > 0.5:
                        signals.update_avatar.emit("wide")
                    elif volume > 0.15:
                        signals.update_avatar.emit("open")
                    else:
                        signals.update_avatar.emit("closed")

                time.sleep(0.04)

            pygame.mixer.music.stop()
            if signals:
                signals.update_avatar.emit("closed")
            pygame.mixer.music.unload()

            if self._was_interrupted:
                self.resume_text = text
                raise AtlasInterrupted(self._interrupt_text or "stop")

            return self._interrupt_text

        except AtlasInterrupted:
            raise
        except Exception as e:
            print(f"Speaker Error: {e}")
            return None
        finally:
            self.is_speaking = False
            self._stop_event.set()  # Ensure listener thread exits cleanly