import math
import cv2
import datetime
from easyocr import Reader

url = "rtsp://pei:5g-mobix@10.0.19.202:554"


def connectToCam():
    cap = cv2.VideoCapture(url, cv2.CAP_ANY)
    now = datetime.datetime.now()
    return cap, now


cap, startDate = connectToCam()
fps = cap.get(cv2.CAP_PROP_FPS)

while True:
    ret, frame = cap.read()
    if not ret:
        cap, startDate = connectToCam()
        fps = cap.get(cv2.CAP_PROP_FPS)
        continue
    else:
        frameId = cap.get(1)
        camtime = cap.get(cv2.CAP_PROP_POS_MSEC)
        if frameId % math.floor(fps) == 0:
            image_time = frame[50:125, 1725:2250]
            cv2.imshow("Current frame", image_time)
            print(Reader(['en']).readtext(image_time, detail=0))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
