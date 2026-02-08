from flask import Flask, request
import RPi.GPIO as GPIO
import time

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

def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()

    timeout_start = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
        if time.time() - timeout_start > 0.02: return 999

    timeout_start = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
        if time.time() - timeout_start > 0.02: return 999

    TimeElapsed = StopTime - StartTime
    return (TimeElapsed * 34300) / 2

def stop():
    GPIO.output(IN1, False); GPIO.output(IN2, False); GPIO.output(IN3, False); GPIO.output(IN4, False)

def forward():
    GPIO.output(IN1, True); GPIO.output(IN2, False); GPIO.output(IN3, True); GPIO.output(IN4, False)

def backward():
    GPIO.output(IN1, False); GPIO.output(IN2, True); GPIO.output(IN3, False); GPIO.output(IN4, True)

def left():
    GPIO.output(IN1, False); GPIO.output(IN2, True); GPIO.output(IN3, True); GPIO.output(IN4, False)

def right():
    GPIO.output(IN1, True); GPIO.output(IN2, False); GPIO.output(IN3, False); GPIO.output(IN4, True)

@app.route("/move", methods=["POST"])
def move():
    action = request.form.get("action")
    dist = distance()

    if dist < 20 and action == "forward":
        stop()
        print(f"WWW: Przeszkoda ({dist:.2f} cm)!")
        return "obstacle", 200

    if action == "forward": forward()
    elif action == "backward": backward()
    elif action == "left": right()
    elif action == "right": left()
    elif action == "stop": stop()
        
    return "", 204

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8080, debug=False, threaded=True) 
    except KeyboardInterrupt:
        print("Program zakończony.")
    finally:
        GPIO.cleanup()