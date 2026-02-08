from flask import Flask, request, Response
import RPi.GPIO as GPIO
import time
import io
from threading import Condition
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

IN1 = 8
IN2 = 10
IN3 = 38
IN4 = 40

GPIO_TRIGGER = 16
GPIO_ECHO = 18

GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

app = Flask(__name__)
camera = None
streaming_output = None

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

def initialize_camera():
    global camera, streaming_output
    try:
        available_cameras = Picamera2.global_camera_info()
        if not available_cameras:
            print("!!! Picamera2 NIE ZNALAZŁO KAMER.")
            camera = None
            return

        print(f"Dostępne kamery: {available_cameras}")
        camera = Picamera2()

        # Konfiguracja wideo (320x240, 15 fps)
        video_config = camera.create_video_configuration(
            main={"size": (320, 240), "format": "RGB888"}, 
            controls={"FrameRate": 15}
        )
        
        camera.configure(video_config)
        
        streaming_output = StreamingOutput()
        camera.start_recording(JpegEncoder(), FileOutput(streaming_output))
        print("Kamera zainicjalizowana.")
    except Exception as e:
        print(f"Błąd kamery: {e}")
        camera = None

# --- FUNKCJE RUCHU I CZUJNIKÓW ---
def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()

    timeout_start = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
        if time.time() - timeout_start > 0.02:
            return 999

    timeout_start = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
        if time.time() - timeout_start > 0.02:
            return 999

    TimeElapsed = StopTime - StartTime
    distance_cm = (TimeElapsed * 34300) / 2
    return distance_cm

def stop():
    GPIO.output(IN1, False)
    GPIO.output(IN2, False)
    GPIO.output(IN3, False)
    GPIO.output(IN4, False)

def forward():
    GPIO.output(IN1, True)
    GPIO.output(IN2, False)
    GPIO.output(IN3, True)
    GPIO.output(IN4, False)

def backward():
    GPIO.output(IN1, False)
    GPIO.output(IN2, True)
    GPIO.output(IN3, False)
    GPIO.output(IN4, True)

def left():
    GPIO.output(IN1, False)
    GPIO.output(IN2, True)
    GPIO.output(IN3, True)
    GPIO.output(IN4, False)

def right():
    GPIO.output(IN1, True)
    GPIO.output(IN2, False)
    GPIO.output(IN3, False)
    GPIO.output(IN4, True)

# --- ROUTING FLASK ---
@app.route("/move", methods=["POST"])
def move():
    action = request.form.get("action")
    dist = distance()

    if dist < 20 and action == "forward":
        stop()
        print(f"WWW: Przeszkoda ({dist:.2f} cm)!")
        return "obstacle", 200

    if action == "forward":
        forward()
    elif action == "backward":
        backward()
    elif action == "left":
        right()
    elif action == "right":
        left()
    elif action == "stop":
        stop()
        
    return "", 204

@app.route('/video_feed')
def video_feed():
    if not camera or not streaming_output:
        return Response("Kamera niedostępna.", status=503)

    def generate():
        while True:
            with streaming_output.condition:
                streaming_output.condition.wait()
                frame = streaming_output.frame
            if frame is None: 
                time.sleep(0.01)
                continue
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    response = Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    initialize_camera()
    
    try:
        app.run(host="0.0.0.0", port=8080, debug=False, threaded=True) 
    except KeyboardInterrupt:
        print("Program zakończony.")
    finally:
        if camera:
            try:
                camera.stop_recording()
                camera.close()
            except Exception: pass
        GPIO.cleanup()