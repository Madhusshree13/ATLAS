# from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QComboBox
# from PyQt6.QtCore import Qt, pyqtSignal
# from PyQt6.QtGui import QPixmap
# import os

# class AtlasControlPanel(QWidget):
#     settings_changed = pyqtSignal(str, str) # Sends (character_name, voice_model_path)

#     def __init__(self, root_path):
#         super().__init__()
#         self.root = root_path
#         self.char_list = ["default", "robot", "engineer"] # Folder names in assets/avatars/
#         self.current_char_idx = 0
#         self.initUI()

#     def initUI(self):
#         self.setWindowTitle("Atlas Control Panel")
#         self.setFixedSize(400, 500)
#         self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
#         self.setStyleSheet("background-color: #1e1e1e; color: white; font-family: Arial;")

#         layout = QVBoxLayout()

#         # --- CHARACTER SELECTION ---
#         char_label = QLabel("Select Avatar")
#         char_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         layout.addWidget(char_label)

#         h_layout = QHBoxLayout()
#         self.btn_left = QPushButton("<")
#         self.btn_right = QPushButton(">")
        
#         self.preview_img = QLabel()
#         self.update_preview()

#         h_layout.addWidget(self.btn_left)
#         h_layout.addWidget(self.preview_img)
#         h_layout.addWidget(self.btn_right)
#         layout.addLayout(h_layout)

#         # --- VOICE SELECTION ---
#         layout.addWidget(QLabel("Select Voice"))
#         self.voice_dropdown = QComboBox()
#         # Automatically list all .onnx files in your voice folder
#         voice_path = os.path.join(self.root, "assets", "voice_models")
#         if os.path.exists(voice_path):
#             voices = [f for f in os.listdir(voice_path) if f.endswith(".onnx")]
#             self.voice_dropdown.addItems(voices)
#         layout.addWidget(self.voice_dropdown)

#         # --- SAVE BUTTON ---
#         self.save_btn = QPushButton("Apply Settings")
#         self.save_btn.clicked.connect(self.apply_settings)
#         layout.addWidget(self.save_btn)

#         self.setLayout(layout)

#         # Connect Arrows
#         self.btn_left.clicked.connect(lambda: self.change_char(-1))
#         self.btn_right.clicked.connect(lambda: self.change_char(1))

#     def update_preview(self):
#         char_name = self.char_list[self.current_char_idx]
#         img_path = os.path.join(self.root, "assets", "avatars", char_name, "atlas_transparent.png")
#         if os.path.exists(img_path):
#             pixmap = QPixmap(img_path)
#             self.preview_img.setPixmap(pixmap.scaled(150, 200, Qt.AspectRatioMode.KeepAspectRatio))

#     def change_char(self, direction):
#         self.current_char_idx = (self.current_char_idx + direction) % len(self.char_list)
#         self.update_preview()

#     def apply_settings(self):
#         char = self.char_list[self.current_char_idx]
#         voice = self.voice_dropdown.currentText()
#         self.settings_changed.emit(char, voice)
#         self.hide()

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QComboBox, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import os
import subprocess
import threading

MODERN_STYLE = """
    QWidget {
        background-color: #0F0F0F; /* Deep midnight black */
        color: #E0E0E0;            /* Soft white text */
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    
    QLabel#Title {
        font-size: 22px;
        font-weight: bold;
        color: #00E5FF;           /* Cyber-cyan accent */
        padding-bottom: 10px;
        border-bottom: 1px solid #333;
    }
    
    QFrame {
        border: 1px solid #2A2A2A;
        border-radius: 15px;
        background-color: #161616;
    }

    QPushButton {
        background-color: #252525;
        border: 1px solid #3A3A3A;
        border-radius: 8px;
        padding: 12px;
        font-weight: bold;
        min-height: 20px;
    }

    QPushButton:hover {
        background-color: #333333;
        border-color: #00E5FF;
        color: #00E5FF;
    }

    QPushButton#Arrow {
        font-size: 24px;
        color: #00E5FF;
        min-width: 50px;
        background-color: transparent;
        border: none;
    }

    QPushButton#Arrow:hover {
        color: #FFFFFF;
        background-color: #1A1A1A;
    }

    QComboBox {
        background-color: #1A1A1A;
        border: 1px solid #333;
        border-radius: 5px;
        padding: 8px;
        color: #00E5FF;
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 15px;
        border-left-width: 1px;
        border-left-color: #333;
        border-left-style: solid;
    }

    /* Style for the 'Sync Systems' button */
    QPushButton#ApplyBtn {
        background-color: #00E5FF;
        color: #000000;
        border: none;
        font-size: 16px;
        letter-spacing: 1px;
    }

    QPushButton#ApplyBtn:hover {
        background-color: #00B8D4;
    }
"""

class AtlasControlPanel(QWidget):
    settings_changed = pyqtSignal(str, str)

    def __init__(self, root_path):
        super().__init__()
        self.root = root_path
        self.char_list = ["default", "Dog", "Duck", "Adult Male","Adult Female"] # Your character folders
        self.current_char_idx = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Atlas Command Center")
        self.resize(600, 750)
        self.setStyleSheet(MODERN_STYLE)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("SYSTEM CONFIGURATION")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # --- CAROUSEL SECTION ---
        carousel_frame = QFrame()
        carousel_layout = QHBoxLayout(carousel_frame)

        self.btn_left = QPushButton("<")
        self.btn_left.setObjectName("Arrow")
        
        self.preview_img = QLabel()
        self.preview_img.setFixedSize(300, 400)
        self.preview_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_right = QPushButton(">")
        self.btn_right.setObjectName("Arrow")

        carousel_layout.addWidget(self.btn_left)
        carousel_layout.addWidget(self.preview_img)
        carousel_layout.addWidget(self.btn_right)
        main_layout.addWidget(carousel_frame)

        self.char_name_label = QLabel("")
        self.char_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.char_name_label.setStyleSheet("font-size: 18px; color: #BBB;")
        main_layout.addWidget(self.char_name_label)

        # --- VOICE SECTION ---
        main_layout.addSpacing(20)
        main_layout.addWidget(QLabel("PRIMARY VOICE NEURAL MODEL"))
        
        self.voice_dropdown = QComboBox()
        voice_path = os.path.join(self.root, "assets", "voice_models")
        if os.path.exists(voice_path):
            voices = [f for f in os.listdir(voice_path) if f.endswith(".onnx")]
            self.voice_dropdown.addItems(voices)
        main_layout.addWidget(self.voice_dropdown)

        # --- ACTION BUTTONS ---
        btn_layout = QHBoxLayout()
        self.preview_voice_btn = QPushButton("Listen to Voice")
        self.save_btn = QPushButton("SYNC SYSTEMS")
        self.save_btn.setStyleSheet("background-color: #00E5FF; color: black; font-weight: bold;")
        
        btn_layout.addWidget(self.preview_voice_btn)
        btn_layout.addWidget(self.save_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # Bind events
        self.btn_left.clicked.connect(lambda: self.change_char(-1))
        self.btn_right.clicked.connect(lambda: self.change_char(1))
        self.save_btn.clicked.connect(self.apply_settings)
        self.preview_voice_btn.clicked.connect(self.preview_voice)

        self.update_display()
        self.hide()

    def update_display(self):
        char = self.char_list[self.current_char_idx]
        self.char_name_label.setText(f"Active Profile: {char.upper()}")
        
        img_path = os.path.join(self.root, "assets", "avatars", char, "atlas_transparent.png")
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            self.preview_img.setPixmap(pixmap.scaled(300, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def change_char(self, direction):
        self.current_char_idx = (self.current_char_idx + direction) % len(self.char_list)
        self.update_display()

    def preview_voice(self):
        """Play a short sample of the selected voice model in a background thread."""
        voice = self.voice_dropdown.currentText()
        if not voice:
            return
        piper_exe  = os.path.join(self.root, "assets", "piper_windows_amd64", "piper", "piper.exe")
        model_path = os.path.join(self.root, "assets", "voice_models", voice)
        temp_wav   = os.path.join(self.root, "assets", "piper_windows_amd64", "piper", "preview_speech.wav")
        sample_text = "Hello, I am Atlas. Ready to assist you."

        def _run():
            try:
                proc = subprocess.Popen(
                    [piper_exe, "--model", model_path, "--output_file", temp_wav],
                    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                proc.communicate(input=sample_text.encode("utf-8"))
                proc.wait()
                if os.path.exists(temp_wav):
                    subprocess.Popen(["powershell", "-c", f"(New-Object Media.SoundPlayer '{temp_wav}').PlaySync()"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Voice preview error: {e}")

        threading.Thread(target=_run, daemon=True).start()

    def apply_settings(self):
        char = self.char_list[self.current_char_idx]
        voice = self.voice_dropdown.currentText()
        self.settings_changed.emit(char, voice)
        self.hide()