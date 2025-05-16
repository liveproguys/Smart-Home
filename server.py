import asyncio
from quart import Quart, render_template, request, redirect, url_for, Response, jsonify
import cv2
import io
import time
from PIL import Image
from servo import Servo
app = Quart(__name__)
PASSWORD = "myhome"
ipm = ''
s2=500
s3=500
s4=500
s5=500
s6=500
camera = cv2.VideoCapture(0)
rate_limits = {
    '/video_feed': (1,12),
    '/home': (10,5),
    '/update': (1,5),
    '/video': (10,5),
    "/":(20,5),
}

request_tracker = {}

@app.before_request
async def rate_limit():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    path = request.path
    if path not in rate_limits:
        return

    window, max_requests = rate_limits[path]
    now = time.time()
    key = f"{ip}:{path}"
    if key not in request_tracker:
        request_tracker[key] = (now, 1)
    else:
        last_time, count = request_tracker[key]
        if now - last_time < window:
            if count >= max_requests:
                time.sleep(3)
                return await render_template("error.html"),429
            request_tracker[key] = (last_time, count + 1)
        else:
            request_tracker[key] = (now, 1)
if not camera.isOpened():
    raise RuntimeError("Kamera ochilmadi. Iltimos, ulangani tekshiring.")

async def generate_frames():
    while True:
        try:
            success, frame = camera.read()
            if not success:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            img_io = io.BytesIO()
            image.save(img_io, 'JPEG', quality=90)
            frame_bytes = img_io.getvalue()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Frame generation error: {e}")
            break

@app.route('/', methods=['GET', 'POST'])
async def login():
    global ipm
    ip = request.remote_addr
    if ip == ipm:
        return redirect(url_for("home"))
    
    if request.method == 'POST':
        form = await request.form
        password = form.get('password')
        if password == PASSWORD:
            ipm = ip
            return redirect(url_for('home'))
        else:
            return await render_template("index.html", error="Parol xato")
    return await render_template("index.html", error=None)

@app.route("/update")
async def update():
    global ipm,s2,s3,s4,s5,s6

    ip = request.remote_addr
    if ip != ipm:
        return redirect('/')
    servo=Servo("/dev/ttyUSB0")
    servo_id = request.args.get('servo', type=int)
    action = request.args.get('action')
    joystick = request.args.get('joystick', type=int)

    if servo_id == 1 and action:
        pulse = 800 if action == 'open' else 100
        servo.write(servo_id, pulse)
        return str(pulse)
    
    elif joystick:
        pulse = request.args.get('pulse', type=int)
        print(pulse)
        if joystick == 1:
            if action in ['up', 'down']:
                s2+=(pulse-500)
            elif action in ['left', 'right']:
                s5+=(pulse-500)
        elif joystick == 2:
            if action in ['up', 'down']:
                s4+=(pulse-500)
                s3-=(pulse-500)
            elif action in ['left', 'right']:
                s6+=(pulse-500)
        servo.write(2,1000-s5)
        servo.write(4,s3)
        servo.write(3,s4)
        servo.write(5,s2)
        servo.write(6,s6)
        return str(pulse)
    
    return "Invalid request", 400
@app.route('/video_feed')
async def video_feed():
    global ipm
    ip = request.remote_addr
    if ip != ipm:
        return redirect('/')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/home')
async def home():
    global ipm
    ip = request.remote_addr
    if ip != ipm:
        return redirect('/')
    return await render_template("home.html")
@app.route('/video')
async def video():
    global ipm
    ip = request.remote_addr
    if ip != ipm:
        return redirect('/')
    return await render_template("control.html")
@app.before_serving
async def startup():
    print("Server ishga tushdi...")

@app.after_serving
async def shutdown():
    print("Server to‘xtatildi.")
    camera.release()

async def main():
    await app.run_task(debug=True, host="0.0.0.0", port=80)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        camera.release()
