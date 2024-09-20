import cv2
import numpy as np
import requests

url = 'http://127.0.0.1:5000/video_feed'

# Initialize the video stream from the Flask server
stream = requests.get(url, stream=True)

# Check if the request was successful
if stream.status_code == 200:
    bytes = bytes()
    for chunk in stream.iter_content(chunk_size=1024):
        bytes += chunk
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                cv2.imshow('Video Feed', img)
                if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
                    break
else:
    print("Failed to access the video feed")

cv2.destroyAllWindows()
