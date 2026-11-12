# Spider-Man Web Effect — Live Camera

This starter project uses your webcam to detect the Spider-Man hand gesture and draw glowing white web strands from the index fingertip.

## Open in VS Code
1. Extract this ZIP.
2. Open VS Code.
3. Select **File → Open Folder** and choose `spider_man_web_effect`.
4. Select **Terminal → New Terminal**.

## Install
Run in the VS Code terminal:
```bash
python -m pip install opencv-python mediapipe numpy
```

## Test packages
```bash
python -c "import cv2, mediapipe, numpy; print('Libraries imported')"
```

## Run
```bash
python app.py
```
Allow webcam access if Windows asks.

## Controls
- Q = quit
- W = toggle web effect
- H = show/hide hand landmarks

## Gesture
Hold one hand up with index finger and little finger raised, middle and ring fingers folded, and thumb extended. Keep the hand fully visible and use good lighting.

## Troubleshooting
- If the webcam does not open, change `CAMERA_INDEX = 0` near the top of `app.py` to `1`.
- If you see an error that `mp.solutions.hands` does not exist, your installed MediaPipe package may have a different API. Python 3.11 is a practical fallback for this classic Hands API: install Python 3.11, then run `py -3.11 -m pip install mediapipe==0.10.21 opencv-python numpy` and start with `py -3.11 app.py`.
- This is a visual effect drawn on the webcam image, not a physical web.
