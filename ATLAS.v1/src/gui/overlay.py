# import sys
# import os
# from PyQt6.QtWidgets import QApplication, QLabel, QWidget
# from PyQt6.QtGui import QPixmap
# from PyQt6.QtCore import Qt, QPoint

# class AtlasAvatar(QWidget):
#     def __init__(self, image_path):
#         super().__init__()
#         self.image_path = image_path
#         # We need this to store where the mouse started the drag
#         self.old_pos = None 
#         self.initUI()

#     def initUI(self):
#         # 1. Window Flags: Stay on top, no taskbar icon, transparent background
#         self.setWindowFlags(
#             Qt.WindowType.WindowStaysOnTopHint | 
#             Qt.WindowType.FramelessWindowHint | 
#             Qt.WindowType.Tool
#         )
#         # 2. **CRUCIAL: Enable per-pixel transparency**
#         self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
#         # 3. Add the Image (the label)
#         self.label = QLabel(self)
        
#         # Double-check: Make sure this is a PNG!
#         pixmap = QPixmap(self.image_path)
#         if pixmap.isNull():
#             print(f"Error: Could not load image from {self.image_path}")
#             sys.exit(1)

#         # Scale image (e.g., 300px width)
#         scaled_pixmap = pixmap.scaledToWidth(750, Qt.TransformationMode.SmoothTransformation)
#         self.label.setPixmap(scaled_pixmap)
        
#         # Adjust window size to fit the image
#         self.resize(scaled_pixmap.width(), scaled_pixmap.height())
        
#         # Position: Bottom Right
#         screen = QApplication.primaryScreen().availableGeometry()
#         x = screen.width() - self.width() - 20
#         y = screen.height() - self.height() - 20
#         self.move(x, y)

#     # --- Mouse Event Logic for Dragging ---
    
#     def mousePressEvent(self, event):
#         # """ Detects when the user clicks on the avatar. """
#         if event.button() == Qt.MouseButton.LeftButton:
#             # Save the current mouse position relative to the window
#             self.old_pos = event.globalPosition().toPoint()

#     def mouseMoveEvent(self, event):
#         # """ Tracks the mouse while it is pressed and moving. """
#         if self.old_pos:
#             # Calculate how much the mouse has moved
#             delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
#             # Move the whole Atlas window by that same amount
#             self.move(self.x() + delta.x(), self.y() + delta.y())
#             # Update the old position for the next movement calculation
#             self.old_pos = event.globalPosition().toPoint()

#     def mouseReleaseEvent(self, event):
#         # """ Detects when the user releases the mouse button. """
#         if event.button() == Qt.MouseButton.LeftButton:
#             # Clear the old position, dragging is over
#             self.old_pos = None

#     def show_atlas(self):
#         self.show()
        

#     def hide_atlas(self):
#         self.hide()

# # --- Test Block ---
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
    
#     # Path to your NEW TRANSPARENT PNG!
#     img_path = os.path.abspath("assets/avatars/default/atlas_transparent.png") 
    
#     if not os.path.exists(img_path):
#         print(f"Error: Avatar image not found at {img_path}")
#         sys.exit()

#     avatar = AtlasAvatar(img_path)
#     avatar.show_atlas()
    
#     print("Atlas is now visible, transparent, and draggable. Close this terminal to exit.")
#     sys.exit(app.exec()) 
  
# from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
# from PyQt6.QtCore import Qt, pyqtSlot, QPoint
# from PyQt6.QtGui import QPixmap
# import os

# class AtlasAvatar(QWidget):
#     def __init__(self, root_path):
#         super().__init__()
#         self.root = root_path
#         self.images = {
#             "closed": os.path.join(self.root, "assets", "avatars", "default", "atlas_transparent.png"),
#             "open": os.path.join(self.root, "assets", "avatars", "default", "atlas_mouth_open.png"),
#             "wide": os.path.join(self.root, "assets", "avatars", "default", "atlas_mouth_wide_open.png"),
#             "gesture": os.path.join(self.root, "assets", "avatars", "default", "atlas_hand_gesture.png")
#         }
#         self.old_pos = None # For mouse dragging
#         self.initUI()

#     def initUI(self):
#         self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
#         self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
#         self.layout = QVBoxLayout()
#         self.label = QLabel(self)
#         self.layout.addWidget(self.label)
#         self.setLayout(self.layout)
        
#         self.update_frame("closed")
#         self.resize(1200, 1400)
        
#         # Center initially
#         # screen = QApplication.primaryScreen().geometry()
#         # self.move(int((screen.width() - 800) / 2), int((screen.height() - 1000) / 2))

#     # --- MOUSE DRAG LOGIC ---
#     def mousePressEvent(self, event):
#         if event.button() == Qt.MouseButton.LeftButton:
#             self.old_pos = event.globalPosition().toPoint()

#     def mouseMoveEvent(self, event):
#         if self.old_pos:
#             delta = event.globalPosition().toPoint() - self.old_pos
#             self.move(self.x() + delta.x(), self.y() + delta.y())
#             self.old_pos = event.globalPosition().toPoint()

#     def mouseReleaseEvent(self, event):
#         self.old_pos = None

#     # --- ANIMATION LOGIC ---
#     @pyqtSlot(str)
#     def update_frame(self, state):
#         path = self.images.get(state, self.images["closed"])
#         if os.path.exists(path):
#             pixmap = QPixmap(path)
#             self.label.setPixmap(pixmap.scaledToWidth(600, Qt.TransformationMode.SmoothTransformation))

#     def show_atlas(self):
#         self.show()
#         self.raise_()

#     def hide_atlas(self):
#         self.hide()

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, pyqtSlot, QPoint, QTimer
from PyQt6.QtGui import QPixmap
import os
import sys
import ctypes

class AtlasAvatar(QWidget):
    def __init__(self, root_path):
        super().__init__()
        self.root = root_path
        self.images = {
            "closed": os.path.join(self.root, "assets", "avatars", "default", "atlas_transparent.png"),
            "open": os.path.join(self.root, "assets", "avatars", "default", "atlas_mouth_open.png"),
            "wide": os.path.join(self.root, "assets", "avatars", "default", "atlas_mouth_wide_open.png"),
            "gesture": os.path.join(self.root, "assets", "avatars", "default", "atlas_hand_gesture.png")
        }
        self.old_pos = None
        self.target_width = 800
        self.target_height = 1000
        self._positioned = False  # defer resize/move until first show
        self._topmost_timer = QTimer(self)
        self._topmost_timer.setInterval(500)
        self._topmost_timer.timeout.connect(self._force_topmost)
        self.initUI()

    def initUI(self):
        # Only set flags and attributes here — do NOT call resize() or move().
        # On Windows/Qt6, resize()/move() trigger HWND creation which can flash
        # the window visible even before show() is called. Deferring geometry
        # to the first show_atlas() call keeps the window truly invisible at startup.
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.update_frame("closed")
        # No resize / move / hide — HWND is not created yet, nothing to flash.

    def _ensure_positioned(self):
        """Called once on first show to set size and screen position."""
        if not self._positioned:
            self.resize(self.target_width, self.target_height)
            screen = QApplication.primaryScreen().availableGeometry()
            self.move(
                screen.right()  - self.target_width  - 16,
                screen.bottom() - self.target_height - 16,
            )
            self._positioned = True

    @pyqtSlot(str)
    def update_frame(self, state):
        path = self.images.get(state, self.images["closed"])
        if os.path.exists(path):
            pixmap = QPixmap(path)
            # 3. SCALE THE IMAGE TO THE NEW WIDTH
            self.label.setPixmap(pixmap.scaledToWidth(self.target_width, Qt.TransformationMode.SmoothTransformation))

    # Mouse Drag Logic (Keep this so you can move her around)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    @pyqtSlot(bool)
    def set_visible(self, show: bool):
        """Thread-safe show/hide — always called on the main thread via Qt's event queue."""
        if show:
            self.show_atlas()
        else:
            self.hide_atlas()

    def _force_topmost(self):
        """Re-asserts HWND_TOPMOST via Win32 API.
        Qt's WindowStaysOnTopHint loses effect when another window gains focus on Windows."""
        if sys.platform == "win32" and self.isVisible():
            hwnd = int(self.winId())
            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )

    def show_atlas(self):
        self._ensure_positioned()
        self.show()
        self.raise_()
        self._force_topmost()
        self._topmost_timer.start()

    def hide_atlas(self):
        self._topmost_timer.stop()
        self.hide()