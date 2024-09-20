import cv2
url = 'http://127.0.0.1:5000/video_feed'
cap = cv2.VideoCapture(url)
if not cap.isOpened():
    print("Error: Could not open video stream.")
else:
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Captured Frame', frame)
        print("Frame captured and saved as 'captured_frame.jpg'")
    else:
        print("Error: Could not read frame.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
cap.release()
