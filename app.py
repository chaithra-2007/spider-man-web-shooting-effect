
import cv2
import mediapipe as mp
import numpy as np
import math

# ---------------- CAMERA ----------------

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("Camera not found!")
    exit()

# Full-screen size
DISPLAY_W = 1280
DISPLAY_H = 720

cv2.namedWindow("Spider-Man Web Effect", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Spider-Man Web Effect", DISPLAY_W, DISPLAY_H)

# ---------------- MEDIAPIPE ----------------

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.45,
    min_tracking_confidence=0.50
)

# ---------------- WEB SETTINGS ----------------

shooting = False
shoot_frame = 0
spread_frame = 0

shoot_frames = 8
spread_frames = 24

start_point = (0, 0)
end_point = (0, 0)

web_distance = 210

gesture_count = 0
release_count = 0
gesture_locked = False

# ---------------- DRAW GLOW LINE ----------------

def draw_glow_line(frame, start, end):

    cv2.line(
        frame, start, end,
        (180, 180, 180), 5,
        cv2.LINE_AA
    )

    cv2.line(
        frame, start, end,
        (255, 255, 255), 2,
        cv2.LINE_AA
    )


# ---------------- DRAW SPIDER WEB ----------------

def draw_web(frame, center, radius):

    if radius <= 0:
        return

    cx, cy = center
    spokes = 16
    rings = 7

    # Radial strands
    for i in range(spokes):

        angle = 2 * math.pi * i / spokes

        x = int(cx + radius * math.cos(angle))
        y = int(cy + radius * math.sin(angle))

        cv2.line(
            frame,
            center,
            (x, y),
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    # Circular rings
    for r in range(1, rings + 1):

        ring_radius = int(radius * r / rings)
        points = []

        for i in range(spokes):

            angle = 2 * math.pi * i / spokes

            x = int(cx + ring_radius * math.cos(angle))
            y = int(cy + ring_radius * math.sin(angle))

            points.append([x, y])

        points = np.array(points, dtype=np.int32)

        cv2.polylines(
            frame,
            [points],
            True,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )


# ---------------- MAIN LOOP ----------------

try:

    while True:

        success, frame = cap.read()

        if not success:
            print("Camera frame not received!")
            break

        frame = cv2.flip(frame, 1)

        # Original camera dimensions
        h, w = frame.shape[:2]

        # Resize camera image to fill the display
        display_frame = cv2.resize(
            frame,
            (DISPLAY_W, DISPLAY_H),
            interpolation=cv2.INTER_LINEAR
        )

        # ---------------- HAND DETECTION ----------------

        small_frame = cv2.resize(
            frame,
            (480, 270),
            interpolation=cv2.INTER_LINEAR
        )

        rgb = cv2.cvtColor(
            small_frame,
            cv2.COLOR_BGR2RGB
        )

        rgb.flags.writeable = False
        result = hands.process(rgb)

        gesture_now = False

        if result.multi_hand_landmarks:

            hand = result.multi_hand_landmarks[0]
            lm = hand.landmark

            index_up = lm[8].y < lm[6].y
            middle_down = lm[12].y > lm[10].y
            ring_down = lm[16].y > lm[14].y
            little_up = lm[20].y < lm[18].y

            thumb_out = abs(lm[4].x - lm[5].x) > 0.10

            gesture_now = (
                index_up
                and middle_down
                and ring_down
                and little_up
                and thumb_out
            )

            # ---------------- STABLE GESTURE ----------------

            if gesture_now:

                gesture_count += 1
                release_count = 0

                if gesture_count >= 4 and not gesture_locked:

                    gesture_locked = True

                    # Fingertip position in display coordinates
                    x = int(lm[8].x * DISPLAY_W)
                    y = int(lm[8].y * DISPLAY_H)

                    # Finger direction
                    dx = lm[8].x - lm[6].x
                    dy = lm[8].y - lm[6].y

                    length = math.sqrt(dx * dx + dy * dy)

                    if length > 0:
                        dx /= length
                        dy /= length

                    start_point = (x, y)

                    web_distance = 210

                    end_point = (
                        int(x + dx * web_distance),
                        int(y + dy * web_distance)
                    )

                    shooting = True
                    shoot_frame = 0
                    spread_frame = 0

            else:

                gesture_count = 0
                release_count += 1

                if release_count >= 5:
                    gesture_locked = False

        else:

            gesture_count = 0
            release_count += 1

            if release_count >= 5:
                gesture_locked = False

        # ---------------- WEB SHOOTING ----------------

        if shooting:

            if shoot_frame < shoot_frames:

                progress = (shoot_frame + 1) / shoot_frames

                current_x = int(
                    start_point[0]
                    + (end_point[0] - start_point[0]) * progress
                )

                current_y = int(
                    start_point[1]
                    + (end_point[1] - start_point[1]) * progress
                )

                draw_glow_line(
                    display_frame,
                    start_point,
                    (current_x, current_y)
                )

                shoot_frame += 1

            elif spread_frame < spread_frames:

                progress = (spread_frame + 1) / spread_frames
                smooth_progress = 1 - (1 - progress) ** 2

                radius = int(web_distance * smooth_progress)

                draw_web(
                    display_frame,
                    end_point,
                    radius
                )

                spread_frame += 1

            else:

                draw_web(
                    display_frame,
                    end_point,
                    web_distance
                )

            # Keep strand connected
            draw_glow_line(
                display_frame,
                start_point,
                end_point
            )

        # ---------------- DISPLAY ----------------

        cv2.imshow(
            "Spider-Man Web Effect",
            display_frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:

    cap.release()
    hands.close()
    cv2.destroyAllWindows()

print("Spider-Man Web Effect Closed!")
