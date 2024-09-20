# import cv2
# # import numpy as np
# import threading
# from flask import Flask, send_file, jsonify
# from io import BytesIO
# # import requests
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# frame = None
# # vdo = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# vdo = cv2.VideoCapture(1)

# def core1():
#     global frame, vdo
#     # capture = cv2.VideoCapture()
#     # capture.open(0)
#     # if not capture.isOpened() :
#     while True:
#         ret, frame = vdo.read()
#         if ret:
#             cv2.imshow("show1", frame)
#             cv2.waitKey(1)

# c1 = threading.Thread(target=core1)
# c1.daemon = True
# c1.start()

# @app.route("/image")
# def get_image():
#     global frame
#     _, jpeg = cv2.imencode('.jpg', frame)
#     jpeg_bytes = jpeg.tobytes()
#     image_stream = BytesIO(jpeg_bytes)
#     cv2.imshow("show1", frame)
#     cv2.waitKey(1)
#     return send_file(image_stream, mimetype='image/jpeg', as_attachment=False, download_name='frame.jpg')


# if __name__ == "__main__":
#     app.run(debug=True)

import cv2
import threading
from io import BytesIO
from flask_cors import CORS
from flask import Flask, send_file

app = Flask(__name__)
CORS(app)

frame = None

def FrameSet(new_frame):
    global frame
    frame = new_frame

def FrameGet():
    global frame
    return frame

def core1():
    global frame
    cap = cv2.VideoCapture(1)
    if cap.isOpened():
        ret, frame = cap.read()
        while ret:
            ret, frame = cap.read()
            FrameSet(frame)
            cv2.imshow("camera", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            #if cv2.waitKey(1) != -1:
            #    cv2.imwrite('cap.png', frame)
    cap.release()
    cv2.destroyAllWindows()

@app.route("/image")
def get_image():
    frame = FrameGet()
    if frame is not None:
        _, jpeg = cv2.imencode('.jpg', frame)
        jpeg_bytes = jpeg.tobytes()
        image_stream = BytesIO(jpeg_bytes)
        return send_file(image_stream, mimetype='image/jpeg', as_attachment=False, download_name='frame.jpg')
    return "No frame available"

@app.route("/test")
def test():
    return "test"

if __name__ == "__main__":
    c1 = threading.Thread(target=core1)
    c1.daemon = True
    c1.start()
    app.run(debug=True)




