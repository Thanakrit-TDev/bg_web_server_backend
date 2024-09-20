# V3----------------------------------------------
import cv2
import numpy as np
import requests
from flask import Flask, send_file, request,jsonify
from io import BytesIO
import threading
import os
import signal
import time
import json


app = Flask(__name__)
img = None
running = True

def nothing(x):
    pass

# inital valume
h_min1 = 20
h_max1 = 30
s_min1 = 100
s_max1 = 255
v_min1 = 100
v_max1 = 255
brightness1 = 50
contrast1 = 50
saturation_boost1 = 1
range_detect1 = 50

def core1():
    global img, running, mask, h_min1,h_max1,s_min1,s_max1,v_min1,v_max1,brightness1,contrast1,saturation_boost1,range_detect1
    url = 'http://127.0.0.1:5000/video_feed'
    stream = requests.get(url, stream=True)

    #add new 2/9/2567
    cv2.namedWindow("Yellow Detection")
    cv2.createTrackbar("Hue Min", "Yellow Detection", 20, 179, nothing)
    cv2.createTrackbar("Hue Max", "Yellow Detection", 30, 179, nothing)
    cv2.createTrackbar("Sat Min", "Yellow Detection", 100, 255, nothing)
    cv2.createTrackbar("Sat Max", "Yellow Detection", 255, 255, nothing)
    cv2.createTrackbar("Val Min", "Yellow Detection", 100, 255, nothing)
    cv2.createTrackbar("Val Max", "Yellow Detection", 255, 255, nothing)
    cv2.createTrackbar("Brightness", "Yellow Detection", 50, 100, nothing)
    cv2.createTrackbar("Contrast", "Yellow Detection", 50, 100, nothing)
    cv2.createTrackbar("Saturation Boost", "Yellow Detection", 1, 10, nothing)
    cv2.createTrackbar("range", "Yellow Detection", 1, 1000, nothing)
    #----

    if stream.status_code == 200:
        bytes_data = bytes()
        for chunk in stream.iter_content(chunk_size=1024):
            if not running:
                break
            bytes_data += chunk
            a = bytes_data.find(b'\xff\xd8')
            b = bytes_data.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    #add new 2/9/2567

                    h_min = cv2.getTrackbarPos("Hue Min", "Yellow Detection")
                    h_max = cv2.getTrackbarPos("Hue Max", "Yellow Detection")
                    s_min = cv2.getTrackbarPos("Sat Min", "Yellow Detection")
                    s_max = cv2.getTrackbarPos("Sat Max", "Yellow Detection")
                    v_min = cv2.getTrackbarPos("Val Min", "Yellow Detection")
                    v_max = cv2.getTrackbarPos("Val Max", "Yellow Detection")
                    brightness = cv2.getTrackbarPos("Brightness", "Yellow Detection")
                    contrast = cv2.getTrackbarPos("Contrast", "Yellow Detection")
                    saturation_boost = cv2.getTrackbarPos("Saturation Boost", "Yellow Detection")
                    range_detect = cv2.getTrackbarPos("range", "Yellow Detection")




                    brightness = brightness - 50
                    contrast = contrast / 50.0
                    img = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)
                    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation_boost, 0, 255)
                    lower_yellow = np.array([h_min, s_min, v_min])
                    upper_yellow = np.array([h_max, s_max, v_max])
                    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        if cv2.contourArea(contour) > range_detect:
                            cv2.drawContours(img, [contour], -1, (0, 255, 0), 2)
                            x, y, w, h = cv2.boundingRect(contour)
                            calw = x + w
                            calh = y + h
                            cv2.rectangle(img, (x, y), (calw, calh), (0, 0, 255), 2)
                            img = cv2.putText(img, f'P1:{y}', (calw+10, y), cv2.FONT_HERSHEY_SIMPLEX, 
                                            0.5, (0, 255, 0), 1, cv2.LINE_AA)
                            img = cv2.putText(img, f'P2:{calh}', (calw+10, calh), cv2.FONT_HERSHEY_SIMPLEX, 
                                            0.5, (0, 255, 0), 1, cv2.LINE_AA)
                            po_w_box = y+int((calh-y)/2)
                            cal_px = calh-y
                            img = cv2.putText(img, f'PW:{cal_px} Px', (calw+10, po_w_box), cv2.FONT_HERSHEY_SIMPLEX, 
                                            0.5, (255, 255, 0), 1, cv2.LINE_AA)

                    # cv2.imshow('Video Feed', img)
                    # cv2.imshow('Yellow Detection', mask)
                    # print(h_min,h_max,s_min,s_max,v_min,v_max,brightness,contrast,saturation_boost,range_detect)
                    if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
                        break
    else:
        print("Failed to access the video feed")
    cv2.destroyAllWindows()

@app.route("/Setting_realtime_mask", methods=["POST"])
def Setting_realtime_mask():
    global h_min,h_max,s_min,s_max,v_min,v_max,brightness,contrast,saturation_boost,range_detect
    data_from_app = request.get_json()

    h_min = int(data_from_app["Hue_Min"])
    h_max = int(data_from_app["Hue_Max"])
    s_min = int(data_from_app["Sat_Min"])
    s_max = int(data_from_app["Sat_Max"])
    v_min = int(data_from_app["Val_Min"])
    v_max = int(data_from_app["Val_MAX"])
    brightness = int(data_from_app["Brightness"])
    contrast = int(data_from_app["Contrast"])
    saturation_boost = int(data_from_app["Saturation"])
    range_detect = int(data_from_app["Range"])
    return jsonify({"message": "Settings received successfully"}), 200

@app.route('/vdo')
def index():
    global img
    if img is None:
        return "No image available", 404
    _, jpeg = cv2.imencode('.jpg', img)
    jpeg_bytes = jpeg.tobytes()
    image_stream = BytesIO(jpeg_bytes)
    return send_file(image_stream, mimetype='image/jpeg', as_attachment=False, download_name='frame.jpg')

@app.route('/mask')
def mask_img():
    global mask
    if mask is None:
        return "No image available", 404
    _, jpeg = cv2.imencode('.jpg', mask)
    jpeg_bytes = jpeg.tobytes()
    image_stream = BytesIO(jpeg_bytes)
    return send_file(image_stream, mimetype='image/jpeg', as_attachment=False, download_name='frame.jpg')

@app.route("/")
def test():
    return("ok test",200)

@app.route('/endprogram')
def endprogram():
    global running
    running = False
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Server shutting down..."

def server_run():
    app.run('127.0.0.1', 2545, debug=False)


if __name__ == '__main__':
    # Start the image processing thread
    c1 = threading.Thread(target=core1)
    c1.daemon = True
    c1.start()

    c2 = threading.Thread(target=server_run)
    c2.daemon = True
    c2.start()

    while True:
        time.sleep(1)

    


    

