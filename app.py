from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import pyautogui

app = Flask(__name__)

# Initialize MediaPipe Hands and Webcam
my_hands = mp.solutions.hands.Hands()
drawing_utils = mp.solutions.drawing_utils
webcam = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = webcam.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)
            frame_height, frame_width, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output = my_hands.process(rgb_frame)
            hands = output.multi_hand_landmarks

            if hands:
                for hand in hands:
                    landmarks = hand.landmark
                    x1 = y1 = x2 = y2 = 0
                    for id, landmark in enumerate(landmarks):
                        x = int(landmark.x * frame_width)
                        y = int(landmark.y * frame_height)
                        if id == 8:  # Index finger
                            x1, y1 = x, y
                        if id == 4:  # Thumb
                            x2, y2 = x, y

                    # Calculate distance between thumb and index finger
                    dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 // 4

                    # Control volume based on distance
                    if dist > 30:
                        pyautogui.press("volumeup")
                    elif dist < 25:
                        pyautogui.press("volumedown")

                    # Draw connections
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)

            # Encode the frame for streaming
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
