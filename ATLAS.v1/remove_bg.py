# import cv2
# import numpy as np
# import os

# def grabcut_transparency(input_path, output_path):
#     img = cv2.imread(input_path)
#     if img is None: return

#     # 1. Initialize the mask and background/foreground models
#     mask = np.zeros(img.shape[:2], np.uint8)
#     bgdModel = np.zeros((1, 65), np.float64)
#     fgdModel = np.zeros((1, 65), np.float64)

#     # 2. Define a rectangle that covers the character
#     # We leave a small 5-pixel margin from the edges to tell GrabCut "this is definitely background"
#     height, width = img.shape[:2]
#     rect = (5, 5, width-10, height-10)

#     # 3. Run GrabCut (5 iterations is usually enough for a clean look)
#     cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

#     # 4. Modify the mask so all 'probably background' pixels are 0 and 'foreground' are 1
#     mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    
#     # 5. Smooth the edges (Anti-aliasing) to prevent "staircase" pixels
#     mask2 = cv2.GaussianBlur(mask2 * 255, (5, 5), 0)

#     # 6. Add the Alpha Channel
#     bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
#     bgra[:, :, 3] = mask2

#     cv2.imwrite(output_path, bgra)
#     print(f"Professional transparency applied to {output_path}")

# # Run it
# grabcut_transparency("assets/avatars/default/image.png", "assets/avatars/default/atlas_transparent.png")

import openwakeword
import os

# This command tells the library to download all pre-trained models 
# and the required 'embedding' models into your venv automatically.
print("Downloading Atlas's ear models... please wait.")
openwakeword.utils.download_models()
print("Done! All models are now in your system.")